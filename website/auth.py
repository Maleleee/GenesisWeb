from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import User
from .forms import SignUpForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import requests

auth = Blueprint('auth', __name__)

# OAuth configuration
CLIENT_ID = '992785662567-oeltunnotl5ft2432u206iv9c980emj2.apps.googleusercontent.com'
CLIENT_SECRET = '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'
REDIRECT_URI = 'http://localhost:5000/google-authorized'
AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
SCOPE = 'email profile'

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.userdash'))

    signup_form = SignUpForm()
    login_form = LoginForm()

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'signup' and signup_form.validate_on_submit():
            # Sign-up logic
            email = signup_form.email.data
            username = signup_form.username.data
            password = signup_form.password.data

            user = User.query.filter_by(email=email).first()
            if not user:
                if username == 'admin':
                    new_user = User(email=email, username=username,
                                    password=generate_password_hash(password, method='pbkdf2:sha256'), is_admin=True)
                else:
                    new_user = User(email=email, username=username,
                                    password=generate_password_hash(password, method='pbkdf2:sha256'))
                db.session.add(new_user)
                db.session.commit()
                flash('Account created successfully! You can now sign in.', 'success')
            else:
                flash('Email already exists. Please sign in.', 'error')
        elif form_type == 'login' and login_form.validate_on_submit():
            # Login logic
            email = login_form.email.data
            password = login_form.password.data

            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Logged in successfully!', 'success')
                if user.is_admin:
                    return redirect(url_for('views.admindash'))
                else:
                    return redirect(url_for('views.userdash'))
            else:
                flash('Invalid email or password.', 'error')

    return render_template("signuplogin.html", signup_form=signup_form, login_form=login_form)

@auth.route('/google-login')
def google_login():
    auth_url = f'{AUTHORIZE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&response_type=code'
    return redirect(auth_url)

@auth.route('/google-authorized')
def google_authorized():
    code = request.args.get('code')
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(TOKEN_URL, data=data)
    access_token = response.json().get('access_token')

    # Use the access token to fetch user profile information from Google
    profile_info = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params={'access_token': access_token}).json()
    email = profile_info.get('email')

    # Check if the user exists in your database
    user = User.query.filter_by(email=email).first() # right now users that register through email are identified as "users" by default
    if not user:
        # If the user does not exist, create a new user
        user = User(email=email, is_admin=False)  # Set is_admin to False for common users
        db.session.add(user)
        db.session.commit()

    login_user(user, remember=True)
    flash('Logged in successfully via Google!', 'success')

    # Redirect the user to the appropriate dashboard
    return redirect(url_for('views.userdash'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
