from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, Beneficiaries, Account
import datetime




class RegistrationForm(FlaskForm):
    fullName = StringField('fullName', 
                            validators=[DataRequired(), Length(min=5, max=40)])
    email = StringField('email', 
                            validators=[DataRequired(), Email()])
    username = StringField('username',
                            validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('password',
                            validators=[DataRequired()])
    confirm_password = PasswordField('confirm_password', 
                            validators=[DataRequired(), EqualTo('password')])
    terms = BooleanField('terms', validators=[DataRequired()])

    submit = SubmitField('register')

    
    def validate_email(self, email):
        
        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('Email is already registered.')
    
    
    
    def validate_username(self, username):
        
        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('Username is already taken.')
        


class LoginForm(FlaskForm):
    username = StringField('username',
                            validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('password',
                            validators=[DataRequired()]) 
    remember = BooleanField('remember')
    submit = SubmitField('login')

class DepositForm(FlaskForm):
    years = [('',"--Select Year")]
    current_year = datetime.datetime.now().year
    for i in range(10):
        years.append((current_year+i, str(current_year+i)))
    
    amount = StringField('amount', 
                            validators=[DataRequired(), Length(min=1, max=12) ])
    card_name = StringField('card_name',
                            validators=[DataRequired(), Length(min=5, max=100)]) 
    card_no = StringField('card_no',
                            validators=[DataRequired(), Length(min=16, max=16) ])
    exp_month = SelectField('exp_month', choices=[("","--Select Month"),(1, "01"), (2, "02"), (3, "03"), (4, "04"),],
                         validators=[DataRequired()])
    exp_year = SelectField('exp_year', choices=years,
                            validators=[DataRequired()])
    cvv = StringField('cvv',
                            validators=[DataRequired(), Length(min=3, max=3)])
    # submit = SubmitField('submit')

class BeneficiaryForm(FlaskForm):
    acc_no = StringField('acc_no',
                            validators=[DataRequired(), Length(min=10, max=10)])
    username = StringField('username', 
                            validators=[DataRequired(), Length(min=3, max=20)])
    submit = SubmitField('submit')

    def validate_acc_no(self, acc_no):
        entry = Beneficiaries.query.filter_by(beneficiary_ID=acc_no.data).first()

        if entry:
            raise ValidationError('Account is already added.')


class TransferForm(FlaskForm):
    list=[]
    def __init__(self, user):
        super(TransferForm, self).__init__()
        self.user = user


        ben = Beneficiaries.query.filter_by(list_owner_ID=self.user).all()
        i = 0
        for item in ben:
            user_id = Account.query.filter_by(account_number=item.beneficiary_ID).first().user_id
            name = User.query.filter_by(id=user_id).first().fullName
            self.list.append(i)
            i+=1
        



    beneficiary = SelectField('beneficiary', choices=list,
                                  validators=[DataRequired()])
    
    amount = StringField('amount', 
                                validators=[DataRequired()])

    note = StringField('note',
                                validators=[Length(min=0, max=200)])

class ProfileForm(FlaskForm):
    fullName = StringField('fullName', 
                            validators=[DataRequired(), Length(min=5, max=40)])
    email = StringField('email', 
                            validators=[DataRequired(), Email(), Length(max=100)])
    username = StringField('username',
                            validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('password')
    confirm_password = PasswordField('confirm_password', 
                            validators=[EqualTo('password')])

    # submit = SubmitField('register')

    
    def validate_email(self, email):
        if email.data != current_user.email:        
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is already registered.')
    
    
    
    def validate_username(self, username):
        if username.data != current_user.username:      
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken.')

class ForgotForm(FlaskForm):
    email = StringField('email', 
                            validators=[DataRequired(), Email()])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email..')
    


class ResetPasswordForm(FlaskForm):
    password = PasswordField('password',
                            validators=[DataRequired()])
    confirm_password = PasswordField('confirm_password', 
                            validators=[DataRequired(), EqualTo('password')])