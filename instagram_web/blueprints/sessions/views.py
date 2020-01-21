from app import app
from flask import Blueprint, render_template, request, url_for, flash, redirect
from models import user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user

csrf = CSRFProtect(app)

sessions_blueprint = Blueprint('sessions',
                            __name__,
                            template_folder='templates')

@sessions_blueprint.route("/login")
def login():
    return render_template('sessions/new.html')

@sessions_blueprint.route("/", methods=["POST"])
def login_form():
    username_input = request.form.get("username_email")
    password_input = request.form.get("login_password")

    accounts = user.User.select() #get database
    for account in accounts:
        if username_input == account.username:
            hashed_password = account.password
            result = check_password_hash(hashed_password, password_input)
            if result:
                login_user(account)
                flash('Correct username')
                return render_template('home.html')
            else:
                flash('Wrong username or password')
                password_error = True
                return render_template('sessions/new.html', password_error = password_error)

@sessions_blueprint.route("/logout")
def logout(): 
    logout_user()
    flash('Successfully logout!')
    return render_template('home.html')


