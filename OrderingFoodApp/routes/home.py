#home.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from OrderingFoodApp.models import UserRole

# @home_bp.route('/')
# def index():
#     if not current_user.is_authenticated:
#         return redirect(url_for('customer.index'))
#     if current_user.role == UserRole.ADMIN:
#         return redirect(url_for('admin.index'))
#     if current_user.role == UserRole.OWNER:
#         return redirect(url_for('owner.index'))
#     return redirect(url_for('customer.index'))


# home.py
home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home_page():
    if current_user.is_authenticated:
        if current_user.role == UserRole.ADMIN:
            return redirect(url_for('admin.index'))
        elif current_user.role == UserRole.OWNER:
            return redirect(url_for('owner.index'))
        elif current_user.role == UserRole.CUSTOMER:
            return redirect(url_for('customer.index'))
    return redirect(url_for('customer.index'))




