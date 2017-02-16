from flask import session, redirect, url_for, flash, request
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in') != True:
            flash('You need to log in first.')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function