from flask import Blueprint, render_template, url_for, redirect
from flask_login import login_required, current_user
from . import db
from . models import User
from flask import jsonify
from .models import User

views = Blueprint('views', __name__)

# Main Page
@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("mainpage.html", user=current_user)

# User Dashboard Page
@views.route('/userdash', methods=['GET', 'POST'])
@login_required
def userdash():
    return render_template("userdash.html", user=current_user)

# Admin Dashboard Page
@views.route('/admindash', methods=['GET', 'POST'])
@login_required
def admindash():
    # Only allow admin users to access this page
    if not current_user.is_admin:
        return redirect(url_for('views.userdash'))
    # Fetch user data from the database
    users = User.query.all()
    return render_template("admindash.html", user=current_user, users=users)

# lets u view users in the database just type 127.0.0.1:5000/users
@views.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)


# for database reset
""""
def delete_all_users():
    User.delete_all()
    return jsonify({'message': 'All users have been deleted!'})

from . import create_app

@app.route('/delete_all_users', methods=['DELETE'])
def delete_all_users():
    return delete_all_users()
"""