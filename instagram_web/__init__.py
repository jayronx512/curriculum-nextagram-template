from app import app
from flask import render_template, redirect, request, url_for, flash
from instagram_web.blueprints.users.views import users_blueprint
from flask_assets import Environment, Bundle
from .util.assets import bundles
from models import user
from flask_wtf.csrf import CSRFProtect
# import re
# from werkzeug.security import generate_password_hash

assets = Environment(app)
assets.register(bundles)

app.register_blueprint(users_blueprint, url_prefix="/users")
csrf = CSRFProtect(app)

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route("/")
def home():
    return render_template('home.html')


