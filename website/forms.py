from . import db
from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, FloatField, IntegerField, DateField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Email, EqualTo, Length, NumberRange, Regexp
from datetime import datetime, timedelta

class SignUpForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30), Regexp('^[A-Za-z]*$', message='First name must contain only letters')])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30), Regexp('^[A-Za-z]*$', message='Last name must contain only letters')])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password1', message='Passwords must match')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AccommodationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=128, message='Name must be between 4 and 128 characters')])
    address = StringField('Address', validators=[DataRequired(), Length(max=256)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=512)])
    tags = StringField('Tags', validators=[Length(max=512)])
    images = MultipleFileField('Add Images', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'jpg or png files only!')])
    price = FloatField('Price per Night in ₱', validators=[DataRequired(), NumberRange(min=0, max=100000, message='Price must be between 0 and 100000')])
    guests_limit = IntegerField('Guests Limit (0 for no limit)', validators=[InputRequired(), NumberRange(min=0, max=1000, message='Guests limit must be between 0 and 1000')])
    available_start_date = DateField('Available Start Date', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.today())
    available_end_date = DateField('Available End Date', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.today() + timedelta(days=30))
    submit = SubmitField('Create Accommodation')