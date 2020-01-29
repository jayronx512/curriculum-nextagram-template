from app import app, gateway
from flask import Blueprint, render_template, request, url_for, flash, redirect
from models.payment import Payment
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
import re
import boto3, botocore



csrf = CSRFProtect(app)

payment_blueprint = Blueprint('payment',
                            __name__,
                            template_folder='templates')





@payment_blueprint.route("/")
def payment():
    token = gateway.client_token.generate()
    return render_template('payment/new.html', token = token)

@payment_blueprint.route("/checkout", methods = ["POST"])
def create_purchase(): 
    nonce = request.form.get("nonce")
    amount = request.form.get("dollar")
    result = gateway.transaction.sale({
        "amount": amount,
        "payment_method_nonce": nonce,
        "options": {
            "submit_for_settlement": True
        }
    })

    if result.is_success:
        payment = Payment(payment = amount, user_id = current_user.id, image_id = "1", message = "HELLO")

        if payment.save():
            return redirect(url_for('payment.payment'))
        else:
            return render_template('payment/payment.html')

    else: 
        flash('Transaction failed', 'danger')
        return render_template('payment/new.html')

