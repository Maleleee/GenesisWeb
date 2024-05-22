from flask import Blueprint, render_template, url_for, redirect, request
from flask_login import login_required, current_user
from . import db
from . models import User
from flask import jsonify
from .models import User
import os
from datetime import date

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
@views.route('/userdashv2', methods=['GET', 'POST'])
@login_required
def userdashv2():
    transactions = read_transactions_from_file()
    balance = calculate_account_balance(transactions)
    recent_withdrawal = get_recent_transaction(transactions, 'expense')
    recent_deposit = get_recent_transaction(transactions, 'income')
    return render_template("userdashv2.html", user=current_user, transactions=transactions, balance=balance, recent_withdrawal=recent_withdrawal, recent_deposit=recent_deposit)

# Admin Dashboard Page
@views.route('/admindash', methods=['GET', 'POST'])
@login_required
def admindash():
    # Only allow admin users to access this page
    if not current_user.is_admin:
        return redirect(url_for('views.userdashv2'))
    # Fetch user data from the database
    users = User.query.all()
    return render_template("admindash.html", user=current_user, users=users)

# View Users Page
@views.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)


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
    return redirect(url_for('views.userdashv2'))

    
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
    # Get form data
    amount = float(request.form['amount'])
    
    # Write withdrawal transaction to text file
    write_transaction_to_file(date.today().strftime('%Y-%m-%d'), 'expense', 'Withdrawal', amount, 'withdrawal', 'completed')
    
    # Redirect back to user dashboard
    return redirect(url_for('views.userdashv2'))


#Deposit Form

@views.route('/deposit', methods=['GET'])
@login_required
def show_deposit_form():
    return render_template('deposit_form.html')

# Handle deposit form submission
@views.route('/deposit', methods=['POST'])
@login_required
def deposit():
    # Get form data
    amount = float(request.form['amount'])
    
    # Write deposit transaction to text file
    write_transaction_to_file(date.today().strftime('%Y-%m-%d'), 'income', 'Deposit', amount, 'deposit', 'completed')
    
    # Redirect back to user dashboard
    return redirect(url_for('views.userdashv2'))