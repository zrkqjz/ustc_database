from flask import Flask, render_template, request, url_for, redirect, flash
import click
from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask_bootstrap import Bootstrap
from flask_login import login_required, logout_user
from functools import wraps

app = Flask(__name__, template_folder='templates', static_folder='Anchor-Bootstrap-UI-Kit-master\\assets')
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMIN)(f)


@app.route('/admin')
@login_required


if __name__ == '__main__':
    app.run(debug=True)