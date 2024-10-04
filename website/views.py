from flask import Blueprint, render_template, url_for, redirect, request, session, jsonify
from flask_login import login_required, current_user
from . import db
from .models import User, Transaction, UserActivity, LoginEvent, make_prediction
import os
from datetime import datetime
import numpy as np
import logging

logger = logging.getLogger(__name__)


views = Blueprint('views', __name__)

# Logging of User Activity
def log_user_activity(user_id=None, endpoint=None, method=None, packet_size=0, request_rate=0.0):
    """Logs user activity to the UserActivity table."""
    try:
        # Debug output for tracking
        print(f"Logging activity - User ID: {user_id}, Endpoint: {endpoint}, Method: {method}, "
              f"Packet Size: {packet_size}, Request Rate: {request_rate}")

        activity_log = UserActivity(
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            packet_size=packet_size,
            request_rate=request_rate,
            timestamp=datetime.utcnow()
        )
        db.session.add(activity_log)
        db.session.commit()
        
        print("Activity logged successfully.")
    except Exception as e:
        logger.error(f"Error logging user activity: {e}")
        db.session.rollback()

# Main Page
@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("mainpage.html", user=current_user)

# User Dashboard Page
@views.route('/userdash', methods=['GET', 'POST'])
@login_required
def userdash():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    recent_withdrawal = next((t for t in reversed(transactions) if not t.transaction_type), None)
    recent_deposit = next((t for t in reversed(transactions) if t.transaction_type), None)
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

# View Activity Logs Page
@views.route('/activitylogs', methods=['GET'])
def activity_logs():
    try:
        activities = UserActivity.query.all()  # Fetch all activity logs
        
        # Debug output to inspect the retrieved activities
        print(f"Fetched activities: {activities}")

        return render_template("activitylogs.html", activities=activities)
    except Exception as e:
        logger.error(f"Error fetching activity logs: {e}")
        return render_template("error.html", error=str(e))  # Handle error gracefully


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
        
        log_user_activity(current_user.id, 'withdraw', 'POST', packet_size=int(amount))
    return redirect(url_for('views.userdash'))

# Deposit Form
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

    # Log user activity
    log_user_activity(current_user.id, 'deposit', 'POST', packet_size=int(amount))
    
    return redirect(url_for('views.userdash'))

# MACHINE LEARNING MODEL SECTION
@views.route('/user-activity', methods=['GET'])
def capture_user_activity():
    if current_user.is_authenticated:
        user_id = current_user.id

        # Simulate packet size and request rate (can be enhanced with real data)
        packet_size = len(request.data) if request.data else 100
        last_request_time = session.get('last_request', time.time())
        request_rate = 1 / (time.time() - last_request_time) if last_request_time else 0
        session['last_request'] = time.time()

        # Log user activity
        log_user_activity(user_id=user_id, endpoint=request.endpoint, method=request.method, packet_size=packet_size, request_rate=request_rate)

        # Prepare data for prediction
        user_data = np.array([[packet_size, request_rate]])
        
        # Make prediction using the ML model
        predicted_label = make_prediction(user_data)

        return jsonify({
            'user_id': user_id,
            'packet_size': packet_size,
            'request_rate': request_rate,
            'predicted_label': predicted_label
        })
        
    return jsonify({'status': 'failed', 'message': 'User not logged in'})
