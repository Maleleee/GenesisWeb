from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    is_admin = db.Column(db.Boolean, default=False)
    balance = db.Column(db.Float, default=0.0)
    transactions = relationship('Transaction', backref='user')
    

class LoginEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    status = db.Column(db.String(64)) # online or offline
    

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    transaction_date = db.Column(db.DateTime(timezone=True), default=func.now())
    transaction_type = db.Column(db.Boolean)  # True = deposit, False = withdraw
    amount = db.Column(db.Float)
    status = db.Column(db.Boolean)  # True = success, False = failed