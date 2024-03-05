from . import db
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from datetime import datetime, timedelta

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    accommodations = db.relationship('Accommodation', backref='owner')
    bookings = db.relationship('Booking', backref='user')

class Accommodation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(128))
    address = db.Column(db.String(256))
    description = db.Column(db.String(512))
    tags = db.Column(db.String(512)) # comma separated list of tags, e.g. "pool,beach,city"
    images = db.Column(db.String(512)) # comma separated list of image file names, e.g. "image1.jpg,image2.jpg"
    price = db.Column(db.Float) # price per night
    guests_limit = db.Column(db.Integer) # max number of guests per booking, 0 means no limit
    available_start_date = db.Column(db.DateTime(timezone=True), default=func.now()) # date from which the accommodation is available to book
    available_end_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now() + timedelta(days=30)) # date until which the accommodation is available to book
    bookings = db.relationship('Booking', back_populates='accommodation')
    is_deleted = db.Column(db.Boolean, default=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    accommodation_id = db.Column(db.Integer, db.ForeignKey('accommodation.id'))
    accommodation = db.relationship('Accommodation', back_populates='bookings')
    start_date = db.Column(db.Date)
    nights = db.Column(db.Integer) # no. of nights booked
    guests = db.Column(db.Integer) # no. of guests accomodating if applicable
    price = db.Column(db.Float) # total price for the booking
    created_date = db.Column(db.DateTime(timezone=True), default=func.now())
    cancelled = db.Column(db.Boolean, default=False)