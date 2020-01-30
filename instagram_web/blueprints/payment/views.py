from app import app, gateway
from flask import Blueprint, render_template, request, url_for, flash, redirect
from models.payment import Payment
from models.images import Image
from models.user import User
from flask_wtf.csrf import CSRFProtect
from flask_login import login_user, logout_user, current_user
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os



csrf = CSRFProtect(app)

payment_blueprint = Blueprint('payment',
                            __name__,
                            template_folder='templates')





@payment_blueprint.route("/<img_id>", methods = ["GET"])
def payment(img_id):
    token = gateway.client_token.generate()
    return render_template('payment/new.html', token = token, img_id = img_id)

@payment_blueprint.route("/<img_id>", methods = ["POST"])
def create_purchase(img_id): 
    nonce = request.form.get("nonce")
    amount = request.form.get("dollar")
    message = request.form.get("message")
    result = gateway.transaction.sale({
        "amount": amount,
        "payment_method_nonce": nonce,
        "options": {
            "submit_for_settlement": True
        }
    })
    if result.is_success:
        payment = Payment(payment = amount, donator_id = current_user.id, image_id = img_id, message = message)
        if payment.save():
            image = Image.get_or_none(id = img_id)
            image_owner = User.get_or_none(id = image.user_id)
            message = Mail(
            from_email=current_user.email,
            to_emails= image_owner.email,
            subject= f"Donation from {current_user.username}",
            html_content=f'<strong>A donation of RM{amount} is made on your image{img_id} from {current_user.username}</strong>')

            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(str(e))

            return redirect(url_for('home'))
        else:
            return render_template('payment/new.html')

    else: 
        flash('Transaction failed', 'danger')
        return render_template('payment/new.html')

