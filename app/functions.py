import os
from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, Flask
from app import app, db, bcrypt, mail
from app.forms import RegistrationForm, LoginForm, DepositForm, BeneficiaryForm, TransferForm, ProfileForm, ForgotForm, ResetPasswordForm
from app.models import User, Account, Transactions, Deposit, Transfer, Beneficiaries
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


def get_user_id(account):
     return Account.query.filter_by(account_number=account).first().user_id

def get_full_name(userID):
    return User.query.filter_by(id=userID).first().fullName


def get_account_number(userID):
    return Account.query.filter_by(user_id=userID).first().account_number


def get_transactions(acc_no, transfer=0, deposit=0):
    list = []
    if deposit == 1:
        deposits = Deposit.query.filter_by(account_no=acc_no).all()
        for item in deposits:
            list.append(Transactions.query.filter_by(trans_ID=item.trans_ID).first())
   
    if transfer == 1:
        transfers = Transfer.query.filter( (Transfer.sender_ID==acc_no) | (Transfer.receiver_ID==acc_no)).all()
        for item in transfers:
            x = list.append(Transactions.query.filter_by(trans_ID=item.trans_ID).first())
            # list.append(x)
   

    list.sort(key=lambda trans: trans.trans_date, reverse=True)

    result=[]
    
    for item in list:
        if(item.type == "Deposit"):
            id = get_user_id(item.deposits[0].account_no)
            name2 = get_full_name(id)
            result.append({ "trans_ID": item.trans_ID,
                        "date" : datetime.strftime(item.trans_date, '%Y-%m-%d') ,
                        "type" : item.type,
                        "amount" : item.amount,
                        "from" : item.deposits[0].card_name,
                        "to"   : name2 + " (me)"
             })
        elif(item.type == "Transfer"):
            sender_id = get_user_id(item.transfers[0].sender_ID)
            receiver_id = get_user_id(item.transfers[0].receiver_ID)
            sender_name = get_full_name(sender_id)
            receiver_name = get_full_name(receiver_id)
            if sender_name == current_user.fullName:
                sender_name+=" (me)"
            elif receiver_name == current_user.fullName:
                receiver_name+=" (me)"
            result.append({ "trans_ID": item.trans_ID,
                        "date" :datetime.strftime(item.trans_date, '%Y-%m-%d') ,
                        "type" : item.type,
                        "amount" : item.amount,
                        "from" : sender_name ,
                        "to"   : receiver_name
             })
    return result

