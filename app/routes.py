import os
from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, Flask
from app import app, db, bcrypt, mail
from app.forms import RegistrationForm, LoginForm, DepositForm, BeneficiaryForm, TransferForm, ProfileForm, ForgotForm, ResetPasswordForm
from app.models import User, Account, Transactions, Deposit, Transfer, Beneficiaries
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from app.functions import get_account_number, get_user_id, get_full_name, get_transactions

@app.route("/", methods=["POST", "GET"])
@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()


    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login unsuccessful. Please check username and password", 'danger')
    return render_template('index.html', title="Login",form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()    

    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fullName=form.fullName.data, email=form.email.data, username=form.username.data, password=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        user_id = User.query.order_by(User.id.desc()).first()
        user_id = int(user_id.id)
        acc_no = Account.query.order_by(Account.account_number.desc()).first()
        if acc_no:
            acc_no = int(acc_no.account_number)
            acc_no += 1
            account = Account(account_number=acc_no, user_id=user_id)
            db.session.add(account)
            db.session.commit()
        else:
            acc_no = 1110000001
            account = Account(account_number=acc_no, user_id=user_id)
            db.session.add(account)
            db.session.commit()
        flash('Your account has been created successsfully!!', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html', title="Register", form=form)

@app.route("/home")
@login_required
def home():
    user_id = current_user.id
    acc_no = get_account_number(user_id)
    balance = Account.query.filter_by(user_id=user_id).first().balance
    name = current_user.fullName[: current_user.fullName.index(' ')]

    result = get_transactions(acc_no, transfer=1, deposit=1)
   

    result = result[:3]
    print(len(result))
    return render_template("home/home.html", name=name, acc_no=acc_no, balance=balance, result=result, title="Dashboard")

@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    form = DepositForm()
    if form.validate_on_submit():
        trans = Transactions(type="Deposit", amount=float(form.amount.data))
        db.session.add(trans)
        db.session.commit()

        trans_id = Transactions.query.order_by(Transactions.trans_ID.desc()).first().trans_ID
        trans_id = int(trans_id)

        account = Account.query.filter_by(user_id=current_user.id).first() 
        acc_no = account.account_number
        deposit = Deposit(account_no=acc_no, card_no=form.card_no.data, card_name=form.card_name.data, trans_ID=trans_id)
        db.session.add(deposit)
        db.session.commit()

       
        balance = account.balance
        balance = float(balance)
        amount = Transactions.query.filter_by(trans_ID=trans_id).first().amount
        new_balance = balance + float(amount)
        account.balance = str(new_balance)
        db.session.commit()
        
    

        flash("Deposit successed", 'success')

    current_account = get_account_number(current_user.id)
    result = get_transactions(current_account, deposit=1)
    
      

    return render_template("deposit/deposit.html", form=form, result=result,title="Deposit")

@app.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    account = get_account_number(current_user.id)
    ben = Beneficiaries.query.filter_by(list_owner_ID=account).all()
    list=[]
    user = account
    form = TransferForm(user)
    for item in ben:
        user_id = get_user_id(item.beneficiary_ID)
        name = get_full_name(user_id)
        list.append([user_id, name])
    
 
    if form.validate_on_submit():
        account = Account.query.filter_by(user_id=current_user.id).first() 
        balance = account.balance
        balance = float(balance)

        if float(balance) >= float(form.amount.data):
            trans = Transactions(type="Transfer", amount=float(form.amount.data))
            db.session.add(trans)
            db.session.commit()

            trans_id = Transactions.query.order_by(Transactions.trans_ID.desc()).first().trans_ID
            trans_id = int(trans_id)

            receiver_id = list[int(form.beneficiary.data)][0]
            receiver_account = get_account_number(receiver_id)

            acc_no = account.account_number
            transefer = Transfer(sender_ID=acc_no, receiver_ID=receiver_account, note=form.note.data,  trans_ID=trans_id)
            db.session.add(transefer)
            db.session.commit()

            
            amount = Transactions.query.filter_by(trans_ID=trans_id).first().amount
            new_balance = balance - float(amount)
            account.balance = str(new_balance)
            db.session.commit()
            
            
            receiver_account = Account.query.filter_by(user_id=receiver_id).first()
            balance = float(receiver_account.balance)
            amount = Transactions.query.filter_by(trans_ID=trans_id).first().amount
            new_balance = balance + float(amount)
            receiver_account.balance = str(new_balance)
            db.session.commit()
            
            flash("Successs", 'success')
        
        else:
            flash("Sorry!! No enough balance", 'danger')

    
    current_account = get_account_number(current_user.id)
    result = get_transactions(current_account, transfer=1)
    


    return render_template("transfer/Transfer.html", form=form, ben=list, result=result, title="Transfer")

@app.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    
    
    current_account = get_account_number(current_user.id)

    result = get_transactions(current_account, transfer=1, deposit=1)


    return render_template("/transactions/transactions.html", result=result, title="Transation")

@app.route("/beneficiaries", methods=["GET", "POST"])
@login_required
def beneficiaries():
    form = BeneficiaryForm()
    owner_id = current_user.id
    owner_account = get_account_number(owner_id)
    if form.validate_on_submit():
    
        acc_no = int(form.acc_no.data)
        ben_id = Account.query.filter_by(account_number=acc_no).first()
        print(owner_account == int(form.acc_no.data))
        
        if owner_account == int(form.acc_no.data):
            flash("You cannot use your own Account Number", 'danger')


        

        elif ben_id:
            if User.query.filter_by(id=ben_id.user_id).first().username == form.username.data:
                ben = Beneficiaries(list_owner_ID=owner_account, beneficiary_ID=int(form.acc_no.data))
                db.session.add(ben)
                db.session.commit()

            else: 
                flash("Account Number and Username does not match", 'danger')
        else:
            flash("Account number is invalid", 'danger')
    elif form.submit.data and not form.validate_on_submit():
        if form.acc_no.errors and form.acc_no.errors[0] == 'Account is already added.':
                flash("Account is already added.", 'danger')
        else:
            flash("Account Could not be added.", 'danger')
    
    list = Beneficiaries.query.filter_by(list_owner_ID=owner_account).all()

    result=[]
    i = 1
    for item in list:
        ben_id = get_user_id(item.beneficiary_ID)
        ben_name = get_full_name(ben_id)
        result.append({ "name": ben_name,
                        "count": i

        })        
        i+=1

    

    return render_template("beneficiaries/beneficiaries.html", form=form, result=result, title="Beneficiaries")

@app.route("/delete_ben/<int:id>", methods=["POST"])
@login_required
def delete_ben(id):
    owner_id = current_user.id
    owner_account = get_account_number(owner_id)
    list = Beneficiaries.query.filter_by(list_owner_ID=owner_account).all()

    result=[]
    i = 1
    for item in list:
        ben_id = get_user_id(item.beneficiary_ID)
        ben_name = get_full_name(ben_id)
        result.append({ "name": ben_name,
                        "count": i

        })        
        i+=1

    del_acc_no = list[id-1].beneficiary_ID 
    q = Beneficiaries.query.filter_by(list_owner_ID=owner_account, beneficiary_ID=del_acc_no ).delete()
    db.session.commit()    
    flash("ben deleted","success")

    return redirect(url_for('beneficiaries'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        current_user.fullName = form.fullName.data
        current_user.email = form.email.data
        current_user.username = form.username.data
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_pwd
        db.session.commit()
        flash('Your account has been updated!!', 'success')
        return redirect(url_for('profile'))
    elif request.method == "GET":
        form.fullName.data = current_user.fullName
        form.email.data = current_user.email
        form.username.data = current_user.username




   
    image_file = url_for('static', filename='login/images/'+ 'bg-01.jpg')
    return render_template('profile/profile.html',  image_file=image_file, form=form, title="Profile")


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset', sender="noreply@arkbank.com", recipients=[user.email])
    msg.body = f''' To reset your password visit the following link:  
    {url_for('reset', token=token, _external=True)}
    
    '''
    mail.send(msg)

@app.route("/forgot/<string:type>", methods=["GET", "POST"])
def forgot(type):
    form = ForgotForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent!!', 'info')
        return redirect(url_for('login'))
    return render_template("forgot.html", title="Forgot", form=form, type=type.upper())

@app.route("/reset/<token>", methods=["GET", "POST"])
def reset(token):

    user = User.verify_token(token)
    if user is None:
        flash('That is invalid or expired token', 'warning')
        return redirect(url_for('forgot', type="password"))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pwd
        db.session.commit()
        flash('Your Password has been updated!!', 'success')
        return redirect(url_for('login'))
    return render_template("reset.html", form=form, title="Reset")