from flask_sqlalchemy import SQLAlchemy
from app import app
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy_utils import PasswordType, Password, EmailType
# from sqlalchemy.ext.automap import automap_base
# from sqlalchemy.orm import Session
# from sqlalchemy import create_engine

# the values of those depend on your setup
POSTGRES_URL = 'localhost:5432'
POSTGRES_USER = 'admin'
POSTGRES_PW = 'admin'
POSTGRES_DB = 'voltadb'
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

db = SQLAlchemy(app)


class Customer(db.Model):

    id = db.Column(db.Integer, db.Sequence('Seq_customer_id', start=10001, increment=1), primary_key=True)
    name = db.Column(db.String(50), nullable= False)
    email = db.Column(db.String(30), nullable= False, unique=True)
    mobile = db.Column(db.String(30), nullable= False, unique=True)
    login = db.Column(db.String(30), nullable= False, unique= True)
    passwd = db.Column(db.String(30), nullable= False)
    avatar = db.Column(db.String(50))
    ev_holded = db.relationship('Ev', backref='Customer', lazy=True)
    wallet_holded = db.relationship('Wallet',backref='Customer', lazy=True)

    def __init__(self, data):
        self.name = data.get('name')
        self.email = data.get('email')
        self.mobile = data.get('mobile')
        self.login = data.get('login')
        self.passwd = data.get('password')
        self.avatar = data.get('avatar_path')

    def __repr__(self):
        return '{"cus_id": %r, "cus_login": %r}' % (self.id, self.login)


class Ev(db.Model):

    ev_id = db.Column(db.Integer, primary_key=True)
    ev_name = db.Column(db.String(50))
    ev_band = db.Column(db.String(15))
    ev_model = db.Column(db.String(30))
    ev_img = db.Column(db.String(30))
    ev_owner = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

    def __init__(self, data):
        # self.ev_id = data.get('ev_id')
        self.ev_name = data.get('ev_name')
        self.ev_band = data.get('ev_band')
        self.ev_model = data.get('ev_model')
        self.ev_img = data.get('ev_img')
        self.ev_owner = data.get('ev_owner')

    def __repr__(self):
        return 'EV : %r' % self.ev_id


class Wallet(db.Model):

    __tablename__ = 'wallet'
    id = db.Column(db.Integer, db.Sequence('Seq_wallet_id', start=10001, increment=1), primary_key=True)
    balance = db.Column(db.Integer, default=0, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('customer.id'), unique=True)
    status = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, data):

        self.id = data.get('id')
        self.balance = data.get('balance')
        self.owner = data.get('owner')
        self.status = data.get('status')

    def withdraw(self, amount):
        self.balance = self.balance - amount

    def deposit(self, amount):
        self.balance = self.balance + amount

    def __repr__(self):
        return 'Wallet ID : %r' % self.id




