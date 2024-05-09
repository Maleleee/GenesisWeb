from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User
from .forms import SignUpForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import requests

auth = Blueprint('auth', __name__)

# OAuth configuration for Google
GOOGLE_CLIENT_ID = '992785662567-oeltunnotl5ft2432u206iv9c980emj2.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
GOOGLE_REDIRECT_URI = 'http://localhost:5000/google-authorized'
GOOGLE_AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_SCOPE = 'email profile'

# OAuth configuration for GitHub
GITHUB_CLIENT_ID = 'Ov23li8BNyKIHZmGnlUm'
GITHUB_CLIENT_SECRET = '941bde3c8ae1aabd8006045249b0a1bfabaffc20'
GITHUB_REDIRECT_URI = 'http://localhost:5000/github-authorized'
GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_SCOPE = 'user:email'

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:  # Check if the user is an admin
            return redirect(url_for('views.admindash'))  # Redirect to admin dashboard
        else:
            return redirect(url_for('views.userdash'))  # Redirect to user dashboard

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
                if user.username == 'admin':
                    user.is_admin = True
                else: 
                    user.is_admin = False
                db.session.commit()
                if user.is_admin:  # Check if the user is an admin
                    return redirect(url_for('views.admindash'))  # Redirect to admin dashboard
                else:
                    return redirect(url_for('views.userdash'))  # Redirect to user dashboard
            else:
                flash('Invalid email or password.', 'error')

    return render_template("signuplogin.html", signup_form=signup_form, login_form=login_form)

@auth.route('/google-login')
def google_login():
    auth_url = f'{GOOGLE_AUTHORIZE_URL}?client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope={GOOGLE_SCOPE}&response_type=code'
    return redirect(auth_url)

@auth.route('/google-authorized')
def google_authorized():
    code = request.args.get('code')
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    access_token = response.json().get('access_token')
    # Use the access token to fetch user profile information from Google
    profile_info = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params={'access_token': access_token}).json()
    email = profile_info.get('email')

    # Check if the user exists in your database
    user = User.query.filter_by(email=email).first()
    if not user:
        # If the user does not exist, create a new user
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    login_user(user, remember=True)
    flash('Logged in successfully via Google!', 'success')
    return redirect(url_for('views.userdash'))

@auth.route('/github-login')
def github_login():
    auth_url = f'{GITHUB_AUTHORIZE_URL}?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}&scope={GITHUB_SCOPE}&response_type=code'
    return redirect(auth_url)

@auth.route('/github-authorized')
def github_authorized():
    code = request.args.get('code')
    data = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code,
        'redirect_uri': GITHUB_REDIRECT_URI
    }
    response = requests.post(GITHUB_TOKEN_URL, data=data, headers={'Accept': 'application/json'})
    access_token = response.json().get('access_token')
    # Use the access token to fetch user profile information from GitHub
    headers = {'Authorization': f'token {access_token}'}
    profile_info = requests.get('https://api.github.com/user', headers=headers).json()
    email = profile_info.get('email')

    # Check if the user exists in your database
    user = User.query.filter_by(email=email).first()
    if not user:
        # If the user does not exist, create a new user
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    login_user(user, remember=True)
    flash('Logged in successfully via GitHub!', 'success')
    return redirect(url_for('views.userdash'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
