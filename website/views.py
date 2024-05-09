from flask import Blueprint, render_template, url_for, redirect
from flask_login import login_required, current_user
from . import db

views = Blueprint('views', __name__)

# ---Main Page---
@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("mainpage.html", user=current_user)

# ---User Dashboard Page---
@views.route('/userdash', methods=['GET', 'POST'])
@login_required
def userdash():
    return render_template("userdash.html", user=current_user)

# ---Admin Dashboard Page---
@views.route('/admindash', methods=['GET', 'POST'])
@login_required
def admindash():
    # Only allow admin users to access this page
    if not current_user.is_admin:
        return redirect(url_for('views.userdash'))
    return render_template("admindash.html", user=current_user)
