from app import app
from flask import Blueprint, render_template, request, url_for, flash, redirect
from models.user import User
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
import re

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

    accounts = User.select() #get database
    for account in accounts:
        if username_input == account.username:
            hashed_password = account.password
            result = check_password_hash(hashed_password, password_input)
            if result:
                login_user(account)
                flash('Correct username')
                # breakpoint()
                return render_template('home.html')
            else:
                flash('Wrong username or password')
                password_error = True
                return render_template('sessions/new.html', password_error = password_error)

@sessions_blueprint.route("/logout", methods=["POST"])
def logout():
    logout_user()
    flash('Successfully logout!')
    return redirect(url_for('home'))
        
@sessions_blueprint.route("/edit")
def edit():
    return render_template('edit.html')

@sessions_blueprint.route("/edit_email")
def edit_email():
    return render_template('sessions/edit_email.html')

@sessions_blueprint.route("/edit_form", methods = ["POST"])
def edit_form(): 
    new_username = request.form.get("new_username")
    check_password = request.form.get("check_password")
    check_retype_password = request.form.get("check_retype_password")
    # breakpoint()
    if current_user.is_authenticated: 
        if check_password == check_retype_password: 
            if check_password_hash(current_user.password, check_password):
                query = User.update(username=new_username).where(User.id == current_user.id)
                # breakpoint()
                if query.execute():
                    flash('Username changed!')
                    return redirect(url_for('home'))

                else:
                    flash('Invalid username input')
                    return render_template('edit.html')
            else:
                flash('Incorrect Password')
                password_error = True
                return render_template('edit.html', password_error = password_error)
        else: 
            flash('Password and retyped password are different')
            password_error = True
            return render_template('edit.html', password_error = password_error)

    else: 
        flash('No user logged in')
        return render_template('edit.html')

@sessions_blueprint.route("/edit_email", methods = ["POST"])
def edit_email_form(): 
    new_email = request.form.get("new_email")
    check_password = request.form.get("check_password")
    check_retype_password = request.form.get("check_retype_password")
    if current_user.is_authenticated: 
        if re.search('[A-Za-z0-9._%+-]+@+[A-Za-z]+[.]+[c][o][m]', new_email) is not None:
            if check_password == check_retype_password: 
                if check_password_hash(current_user.password, check_password):
                    query = User.update(email=new_email).where(User.id == current_user.id)
                    if query.execute():
                        flash('Email changed!')
                        return redirect(url_for('home'))
                    else:
                        flash('Invalid email input')
                        return render_template('sessions/edit_email.html')
                else:
                    flash('Incorrect Password')
                    password_error = True
                    return render_template('sessions/edit_email.html', password_error = password_error)
            else: 
                flash('Password and retyped password are different')
                password_error = True
                return render_template('sessions/edit_email.html', password_error = password_error)
        else: 
            flash('Invalid email')
            password_error = True
            return render_template('sessions/edit_email.html', password_error = password_error)

    else: 
        flash('No user logged in')
        return render_template('sessions/edit_email.html')
        
     
 


