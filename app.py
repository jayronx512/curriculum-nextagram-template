import os
import config
from flask import Flask, render_template
from models.base_model import db
from flask_login import login_manager, LoginManager
from models.user import User
import braintree



web_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'instagram_web')

app = Flask('NEXTAGRAM', root_path=web_dir)


login_manager = LoginManager()
login_manager.init_app(app)

if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")


@app.before_request
def before_request():
    db.connect()


@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        print(db)
        print(db.close())
    return exc

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id= os.environ.get("SB_MERCHANT"),
        public_key= os.environ.get("SB_PUBLIC"),
        private_key= os.environ.get("SB_KEY")
    )
)

# @app.route("/")
# def home():
#     return render_template("home.html")
