from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    acc_no = db.relationship('Account', backref='acc_no', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


    def __repr__(self):
        return f"User('{self.fullName}', '{self.email}', '{self.username}', '{self.image_file}')"

class Account(db.Model):
    account_number = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    balance = db.Column(db.String(12), nullable=False, default='0.00')

    def __repr__(self):
        return f"Account('{self.account_number}', '{self.balance}', '{self.user_id}')"

class Transactions(db.Model):
    trans_ID = db.Column(db.Integer, primary_key=True)
    trans_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(12,2), nullable=False)
    deposits = db.relationship('Deposit', backref='deposits', lazy=True)
    transfers = db.relationship('Transfer', backref='tranfers', lazy=True)

    def __repr__(self):
        return f"Transactions('{self.trans_ID}', '{self.trans_date}', '{self.type}', '{self.amount}')"

class Deposit(db.Model):
    deposit_ID = db.Column(db.Integer, primary_key=True)
    account_no = db.Column(db.Integer, db.ForeignKey('account.account_number'), nullable=False)
    card_no = db.Column(db.String(16), nullable=False)
    card_name = db.Column(db.String(100), nullable=False)
    trans_ID = db.Column(db.Integer, db.ForeignKey('transactions.trans_ID'), nullable=False)

    def __repr__(self):
        return f"Deposit('{self.deposit_ID}', '{self.account_no}', '{self.card_no}', '{self.card_name}', '{self.trans_ID}')"
    
class Transfer(db.Model):
    tranfer_ID = db.Column(db.Integer, primary_key=True)
    sender_ID = db.Column(db.Integer, db.ForeignKey('account.account_number'), nullable=False)
    receiver_ID = db.Column(db.Integer, db.ForeignKey('account.account_number'), nullable=False)
    note = db.Column(db.String(200), nullable=False)
    trans_ID = db.Column(db.Integer, db.ForeignKey('transactions.trans_ID'), nullable=False)

    def __repr__(self):
        return f"Transfer('{self.tranfer_ID}', '{self.sender_ID}', '{self.receiver_ID}', '{self.note}', '{self.trans_ID}')"

class Beneficiaries(db.Model):
    list_owner_ID = db.Column(db.Integer, db.ForeignKey('account.account_number'), primary_key=True)
    beneficiary_ID =  db.Column(db.Integer, db.ForeignKey('account.account_number'), primary_key=True)
    
    def __repr__(self):
        return f"Beneficiaries('{self.list_owner_ID}', '{self.beneficiary_ID}')"
