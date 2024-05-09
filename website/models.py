from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    is_admin = db.Column(db.Boolean, default=False)