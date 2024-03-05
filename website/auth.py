from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from .forms import SignUpForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from . import db # . = __init__.py
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

# ---Login Page---
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))  # Redirect to the home page if already logged in
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Check if the user exists and the password is correct
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash('Invalid email or password.', category='error')

    return render_template("login.html", form=form, user=current_user)

# ---Logout Function---
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    
    return redirect(url_for('auth.login'))

# ---Sign Up Page---
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))  # Redirect to the home page if already logged in
    
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        first_name = form.first_name.data
        password = form.password1.data

        user = User.query.filter_by(email=email).first()
        # Check email is already owned by an existing user
        if user:
            flash('Email already exists.', category='error')
        # If the email does not have an owner, create a new user
        else:
            # Create user instance
            new_user = User(
                email=email,
                first_name=first_name,
                password=generate_password_hash(password, method='pbkdf2:sha256')
            )

            db.session.add(new_user)
            db.session.commit()

            flash('Account created!', category='success')
            return redirect(url_for('auth.login'))
    # If the form is not valid, display the error messages
    else:
        for errorMessages in form.errors.values():
            for err in errorMessages:
                flash(err, category='error')

    return render_template("sign_up.html", form=form, user=current_user)