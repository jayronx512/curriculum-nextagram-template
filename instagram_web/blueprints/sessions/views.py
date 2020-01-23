from app import app
from flask import Blueprint, render_template, request, url_for, flash, redirect
from models.user import User
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
import re
import boto3, botocore



csrf = CSRFProtect(app)

sessions_blueprint = Blueprint('sessions',
                            __name__,
                            template_folder='templates')



# s3 = boto3.client(
#     "s3",
#     aws_access_key_id = S3_KEY,
#     aws_secret_access_key=S3_SECRET
# )
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
                flash('Login successfully!', 'success')
                # breakpoint()
                return redirect(url_for('home'))
            else:
                flash('Wrong username or password', 'danger')
                return render_template('sessions/new.html')
        
    flash('Wrong username or password', 'danger')
    return render_template('sessions/new.html')


@sessions_blueprint.route("/logout", methods=["POST"])
def logout():
    logout_user()
    flash('Successfully logout!', 'success')
    return redirect(url_for('home'))
        



        

# def upload_file_to_s3(file, bucket_name = "jj-clone-instagram", acl="public-read"):

#     try:

#         s3.upload_fileobj(
#             file,
#             bucket_name,
#             file.filename,
#             ExtraArgs={
#                 "ACL": acl,
#                 "ContentType": file.content_type
#             }
#         )

#     except Exception as e:
#         # This is a catch all exception, edit this part to fit your needs.
#         print("Something Happened: ", e)
#         return e
 


