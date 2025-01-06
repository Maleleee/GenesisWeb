from flask import Blueprint, render_template, url_for, redirect, request, session, jsonify, current_app
from flask_login import login_required, current_user
from . import db
from .models import User, Transaction, UserActivity, LoginEvent
from .mlmodel import make_prediction
import os
from datetime import datetime
import numpy as np
import logging
import time
import csv

logger = logging.getLogger(__name__)

views = Blueprint('views', __name__)

# Logging of User Activity
def log_user_activity(user_id=None, endpoint=None, method=None, packet_size=0, request_rate=0.0):
    """Logs user activity to the UserActivity table."""
    try:
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
    if not current_user.is_admin:
        return redirect(url_for('views.userdash'))

    # Fetch attack data from session, default to empty if not present
    attack_data = session.get('attack_data', [])

    recent_login_events = LoginEvent.query.order_by(LoginEvent.timestamp.desc()).limit(10).all()
    users = User.query.all()
    now = datetime.now()
    new_users = [user for user in users if (now - user.date_created).total_seconds() < 24 * 3600]
    total_users = len(users)

    # Emit the initial attack data to connected clients (if needed)
    socketio = current_app.extensions['socketio']  # Access socketio through current_app
    socketio.emit('update_user_data', attack_data)

    return render_template("admindash.html", user=current_user, users=users,
                           recent_login_events=recent_login_events, new_users=new_users,
                           total_users=total_users, attack_data=attack_data)


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
        activities = UserActivity.query.all()
        return render_template("activitylogs.html", activities=activities)
    except Exception as e:
        logger.error(f"Error fetching activity logs: {e}")
        return render_template("error.html", error=str(e))

# Withdraw Route (POST)
@views.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    try:
        amount = float(request.form.get('amount'))
        if current_user.balance < amount:
            return redirect(url_for('views.userdash'))
        else:
            current_user.balance -= amount
            transaction = Transaction(user_id=current_user.id, transaction_type=False, amount=amount, status=True)
            db.session.add(transaction)
            db.session.commit()
            log_user_activity(user_id=current_user.id, endpoint='withdraw', method='POST', packet_size=int(amount))
            return redirect(url_for('views.userdash'))
    except Exception as e:
        logger.error(f"Error in withdraw operation: {e}")
        return redirect(url_for('views.userdash'))

# Deposit Route (POST)
@views.route('/deposit', methods=['POST'])
@login_required
def deposit():
    try:
        amount = float(request.form.get('amount'))
        current_user.balance += amount
        transaction = Transaction(user_id=current_user.id, transaction_type=True, amount=amount, status=True)
        db.session.add(transaction)
        db.session.commit()
        log_user_activity(user_id=current_user.id, endpoint='deposit', method='POST', packet_size=int(amount))
        return redirect(url_for('views.userdash'))
    except Exception as e:
        logger.error(f"Error in deposit operation: {e}")
        return redirect(url_for('views.userdash'))

# MACHINE LEARNING MODEL SECTION
@views.route('/user-activity', methods=['GET'])
def capture_user_activity():
    if current_user.is_authenticated:
        user_id = current_user.id
        packet_size = len(request.data) if request.data else 100

        last_request_time = session.get('last_request', time.time())
        current_time = time.time()
        elapsed_time = current_time - last_request_time
        request_rate = 1 / elapsed_time if elapsed_time > 0 else 0.0
        session['last_request'] = current_time

        log_user_activity(
            user_id=user_id,
            endpoint=request.endpoint,
            method=request.method,
            packet_size=packet_size,
            request_rate=request_rate
        )

        user_data = np.array([[packet_size, request_rate]])

        try:
            predicted_labels = make_prediction(user_data)
            if predicted_labels:
                return jsonify({
                    'user_id': user_id,
                    'packet_size': int(packet_size),
                    'request_rate': float(request_rate),
                    'predicted_labels': predicted_labels
                })
            else:
                return jsonify({'status': 'failed', 'message': 'No valid prediction'}), 400

        except Exception as e:
            logger.error(f"Error in make_prediction: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
        
    return jsonify({'status': 'failed', 'message': 'User not logged in'})

# @views.route('/get_attack_data', methods=['GET'])
# def get_attack_data():
#     csv_file_path = 'attack_data.csv'
#     attack_data = []

#     try:
#         with open(csv_file_path, mode='r') as file:
#             reader = csv.DictReader(file)
#             for row in reader:
#                 attack_data.append(row)
#     except FileNotFoundError:
#         return jsonify({'error': 'File not found'}), 404

#     return jsonify(attack_data)

# Postman Section for testing

@views.route('/get_recent_login_data', methods=['GET'])
def get_recent_login_data():
    recent_login_events = LoginEvent.query.order_by(LoginEvent.timestamp.desc()).all()
    return jsonify([{
        'email': event.email,
        'username': event.username,
        'timestamp': event.timestamp.timestamp()  # Return timestamp as a Unix timestamp
    } for event in recent_login_events])
