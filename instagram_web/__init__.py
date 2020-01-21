from app import app
from flask import render_template, redirect, request, url_for, flash
from instagram_web.blueprints.users.views import users_blueprint
from flask_assets import Environment, Bundle
from .util.assets import bundles
from models import user
import re

assets = Environment(app)
assets.register(bundles)

app.register_blueprint(users_blueprint, url_prefix="/users")

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route("/signup_form", methods=["POST"])
def signup_form():
    username = request.form.get('username')
    email = request.form.get('email')
    while True:
        password = request.form.get('password')
        if len(password) < 6:
            flash('Make sure your password is at least 6 letters')
            password_error = True
            return render_template('signup.html', password_error = password_error)
        elif re.search('[0-9]',password) is None:
            flash('Make sure your password has a number in it')
            password_error = True
            return render_template('signup.html', password_error = password_error)
        elif re.search('[A-Z]', password) is None:
            flash('Make sure your password has a capital letter in it')
            password_error = True
            return render_template('signup.html', password_error = password_error)
        elif re.search("[$&+,:;=?@#\"\\/|'<>.^*()%!-]", password) is None:
            flash('Make sure your password has special character in it')
            password_error = True
            return render_template('signup.html', password_error = password_error)
        else:
            new_user = user.User(username=username, email=email, password=password)
            break
    
    if new_user.save():
        flash('New user created!')
        return redirect('signup')

    else:
        for err in new_user.errors:
            flash(err)
        # flash(user.User.errors[0])
        return render_template('signup.html', errors=new_user.errors)
