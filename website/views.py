from flask import Blueprint, render_template, url_for, redirect, request
from flask_login import login_required, current_user
from . import db
from . models import User, Transaction
from flask import jsonify
from .models import User, LoginEvent
import os
from datetime import datetime, timedelta


views = Blueprint('views', __name__)

# Main Page
@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("mainpage.html", user=current_user)


def get_recent_transaction(transactions, transaction_type):
    for transaction in reversed(transactions):
        if transaction['transaction_type'].lower() == transaction_type:
            return transaction
    return None

# User Dashboard Page
@views.route('/userdash', methods=['GET', 'POST'])
@login_required

def userdash():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    recent_withdrawal = next((t for t in reversed(transactions) if not t.transaction_type), None)
    recent_deposit = next((t for t in reversed(transactions) if t.transaction_type), None)
    print(recent_deposit)
    return render_template("userdash.html", user=current_user, transactions=transactions, balance=current_user.balance, recent_withdrawal=recent_withdrawal, recent_deposit=recent_deposit)

# Admin Dashboard Page
@views.route('/admindash', methods=['GET', 'POST'])
@login_required
def admindash():
    # Only allow admin users to access this page
    if not current_user.is_admin:
        return redirect(url_for('views.userdash'))
    
    # Fetch recent login events from the database
    recent_login_events = LoginEvent.query.order_by(LoginEvent.timestamp.desc()).limit(10).all()

    # Fetch user data from the database
    users = User.query.all()
    
    now = datetime.now()
    new_users = [user for user in users if (now - user.date_created).total_seconds() < 24 * 3600]
    
    total_users = len(users)
    
    return render_template("admindash.html", user=current_user, users=users, recent_login_events=recent_login_events, new_users=new_users, total_users=total_users)

# View Users Page
@views.route('/users')
def users():
    users = User.query.all()
    
    total_users = len(users)
    return render_template('users.html', users=users, total_users=total_users)
    
# Withdraw Page
@views.route('/withdraw', methods=['GET'])
@login_required
def show_withdraw_form():
    return render_template('withdraw_form.html')

@views.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    amount = float(request.form.get('amount'))
    if current_user.balance < amount:
        return render_template('withdraw_form.html')
    else:
        current_user.balance -= amount
        transaction = Transaction(user_id=current_user.id, transaction_type=False, amount=amount, status=True)
        db.session.add(transaction)
        db.session.commit()
    return redirect(url_for('views.userdash'))

#Deposit Form

@views.route('/deposit', methods=['GET'])
@login_required
def show_deposit_form():
    return render_template('deposit_form.html')

@views.route('/deposit', methods=['POST'])
@login_required
def deposit():
    amount = float(request.form.get('amount'))
    current_user.balance += amount
    transaction = Transaction(user_id=current_user.id, transaction_type=True, amount=amount, status=True)
    db.session.add(transaction)
    db.session.commit()
    return redirect(url_for('views.userdash'))