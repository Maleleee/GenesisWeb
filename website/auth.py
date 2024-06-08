from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, session
from .models import User, LoginEvent
from .forms import SignUpForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail, auth
from flask_login import login_user, login_required, logout_user, current_user
import requests
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Message, Mail
from datetime import datetime
import re
import dns.resolver

EMAIL_REGEX = r'^[\w\.-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'


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
        if current_user.is_admin:  
            return redirect(url_for('views.admindash'))  
        else:
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

            if not is_valid_email(email):
                flash('Invalid email domain. Please use a valid email address.', 'error')
                return redirect(url_for('auth.login'))

            user = User.query.filter_by(email=email).first()
            if user:
                flash('This email already has an account. Please use a different email.', 'error')
                return redirect(url_for('auth.login'))

            new_user = User(
                email=email,
                username=username,
                password=generate_password_hash(password, method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! You can now sign in.', 'success')
        elif form_type == 'login' and login_form.validate_on_submit():
            # Login logic
            email = login_form.email.data
            password = login_form.password.data

            user = User.query.filter_by(email=email).first()
            if user and user.password is not None and check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Logged in successfully!', 'success')

                timestamp = datetime.now()

                # Login Event
                login_event = LoginEvent(
                    email=user.email,
                    username=user.username,
                    timestamp=timestamp,
                    status='online'
                )
                db.session.add(login_event)
                db.session.commit()

                user.is_admin = (user.username == 'admin')
                db.session.commit()

                if user.is_admin:  
                    return redirect(url_for('views.admindash'))  
                else:
                    return redirect(url_for('views.userdash'))  
            else:
                flash('Invalid email or password.', 'error')

    return render_template("signuplogin.html", signup_form=signup_form, login_form=login_form)


def is_valid_email(email):
    allowed_domains = [
        'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'aol.com',
        'icloud.com', 'live.com', 'msn.com', 'protonmail.com', 'zoho.com'
        # Add more popular domains as needed
    ]

    domain = email.split('@')[-1]

    if domain in allowed_domains:
        return True
    else:
        return False


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
    response_data = response.json()

    # Check if access token is present in the response
    access_token = response_data.get('access_token')
    if not access_token:
        flash('Failed to retrieve access token from Google. Please try again.', 'error')
        return redirect(url_for('auth.login'))

    # Fetch user profile information from Google using the access token
    profile_info = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params={'access_token': access_token}).json()
    email = profile_info.get('email')

    if not email:
        flash('Failed to retrieve email from Google. Please try again.', 'error')
        return redirect(url_for('auth.login'))

    # Check if the user exists in your database
    user = User.query.filter_by(email=email).first()
    if user:
        # If the user exists, log them in
        login_user(user, remember=True)
        flash('Logged in successfully via Google!', 'success')
    else:
        # If the user does not exist, create a new user
        username = email.split('@')[0]  # Use the part of the email before '@' as the default username
        user = User(email=email, username=username, password=None)  # Set password to None or a default value if required
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        flash('Account created and logged in successfully via Google!', 'success')
    
    login_event = LoginEvent(email=email, username=user.username, timestamp=datetime.utcnow())
    db.session.add(login_event)
    db.session.commit()

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
    response_data = response.json()

    # Check if access token is present in the response
    access_token = response_data.get('access_token')
    if not access_token:
        flash('Failed to retrieve access token from GitHub. Please try again.', 'error')
        return redirect(url_for('auth.login'))

    # Fetch user profile information from GitHub using the access token
    headers = {'Authorization': f'token {access_token}'}
    profile_info = requests.get('https://api.github.com/user', headers=headers).json()
    email = profile_info.get('email')

    if not email:
        flash('GitHub did not provide your email address. Please grant access to your email when logging in.', 'error')
        return redirect(url_for('auth.login'))

    # Check if the email domain is valid
    if not is_valid_email(email):
        flash('Invalid email domain. Please use a valid email address.', 'error')
        return redirect(url_for('auth.login'))

    # Check if the user exists in your database
    user = User.query.filter_by(email=email).first()
    if not user:
        # If the user does not exist, create a new user
        username = email.split('@')[0]  # Use the part of the email before '@' as the default username
        user = User(email=email, username=username, password=None)  # Set password to None or a default value if required
        db.session.add(user)
        db.session.commit()

    login_user(user, remember=True)
    flash('Logged in successfully via GitHub!', 'success') 
    
    login_event = LoginEvent(email=email, username=user.username, timestamp=datetime.utcnow())
    db.session.add(login_event)
    db.session.commit()
    
    return redirect(url_for('views.userdash'))


def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    error = None
    success = None
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user is None:
            error = "The email you entered does not exist!"
        else:
            sec = get_serializer()
            token = sec.dumps(email, salt='email-confirm')
            msg = Message('Genesis Account Password Reset Request', sender='infogenesis.communications@gmail.com', recipients=[email])
            link = url_for('auth.reset_password', token=token, _external=True)
            msg.body = f"""
            Hello,

            We have received a request to reset the password for your Genesis account: {email}

            If you submitted this request, please click the button below to proceed:

            {link}
            """
            mail.send(msg)
            success = "Successfully sent! Kindly check your email."
    return render_template('forgotpass.html', error=error, success=success)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    sec = get_serializer()
    try:
        email = sec.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return render_template('reset_password.html', token=token, error="The passwords do not match")
        user = User.query.filter_by(email=email).first()
        user.password = generate_password_hash(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', token=token)

@auth.route('/logout')
@login_required
def logout():
    # Logout logic
    # Update status to "offline" when user logs out
    user_id = session.get('user_id')
    if user_id:
        login_event = LoginEvent.query.filter_by(user_id=user_id, status='online').first()
        if login_event:
            login_event.status = 'offline'
            db.session.commit()
    
    session.clear()  # Clear session data
    logout_user()
    
    return redirect(url_for('auth.login'))  # Redirect to login page after logout
