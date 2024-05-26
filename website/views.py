from flask import Blueprint, render_template, url_for, redirect, request
from flask_login import login_required, current_user
from . import db
from . models import User, Transaction
from flask import jsonify
from .models import User, LoginEvent
import os
from datetime import datetime, timedelta



TRANSACTION_FILE = 'transactions.txt'
DEFAULT_BALANCE = 500000

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


def save_balance_to_file(balance):
    with open('balance.txt', 'w') as file:
        file.write(str(balance))


#Show transaction form
@views.route('/make_transaction', methods=['POST'])
@login_required
def make_transaction():
    # Get form data
    date = request.form['date']
    transaction_type = request.form['transaction_type']
    description = request.form['description']
    amount = float(request.form['amount'])
    category = request.form['category']
    status = request.form['status']
    
    # Write transaction data to text file
    write_transaction_to_file(date, transaction_type, description, amount, category, status)
    
    # Redirect back to user dashboard
    return redirect(url_for('views.userdash'))

    
# Function to calculate the account balance
def calculate_account_balance(transactions):
    balance = DEFAULT_BALANCE
    for transaction in transactions:
        if transaction['transaction_type'].lower() == 'income':
            balance += transaction['amount']
        elif transaction['transaction_type'].lower() == 'expense':
            balance -= transaction['amount']
    return balance

# Function to write transaction data to a text file
def write_transaction_to_file(date, transaction_type, description, amount, category, status):
    with open(TRANSACTION_FILE, 'a') as file:
        file.write(f"{date},{transaction_type},{description},{amount},{category},{status}\n")

# Function to read transactions from the text file
def read_transactions_from_file():
    transactions = []
    if os.path.exists(TRANSACTION_FILE):
        with open(TRANSACTION_FILE, 'r') as file:
            for line in file:
                date, transaction_type, description, amount, category, status = line.strip().split(',')
                transactions.append({
                    'date': date,
                    'transaction_type': transaction_type,
                    'description': description,
                    'amount': float(amount),
                    'category': category,
                    'status': status
                })
    return transactions



@views.route('/make_transaction', methods=['GET'])
@login_required
def show_transaction_form():
    return render_template('transaction_form.html')


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
        #Lagyan na lang ng message na not enough balance
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