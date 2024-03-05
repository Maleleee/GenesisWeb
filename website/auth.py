from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User
from .forms import SignUpForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from . import db # . = __init__.py
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

# ---Sign-up/Login Page---
@auth.route('login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.userdash'))  # Redirect to the main page if already logged in
    
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
                if username == 'admin': # Create admin account if username is 'admin', for testing
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

# ---Logout Function---
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    
    return redirect(url_for('auth.login'))
