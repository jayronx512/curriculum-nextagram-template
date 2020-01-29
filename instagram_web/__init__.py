from app import app
from flask import render_template, redirect, request, url_for, flash, Flask
from instagram_web.blueprints.users.views import users_blueprint
from instagram_web.blueprints.sessions.views import sessions_blueprint
from instagram_web.blueprints.payment.views import payment_blueprint
from flask_assets import Environment, Bundle
from .util.assets import bundles
from models import user
from flask_wtf.csrf import CSRFProtect

# import re
# from werkzeug.security import generate_password_hash

assets = Environment(app)
assets.register(bundles)

app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(sessions_blueprint, url_prefix="/sessions")
app.register_blueprint(payment_blueprint, url_prefix="/payment")
csrf = CSRFProtect(app)


@app.errorhandler(404)
def internal_server_error(e):
    return render_template('404.html'), 404


@app.route("/")
def home():
    return render_template('home.html')



