from flask_login import current_user
from flask import flash


def min_clearance(clearance: int):
    authorized = current_user.is_authenticated and current_user.clearance >= clearance
    if not authorized:
        flash('Unauthorized.', 'danger')
    return authorized
