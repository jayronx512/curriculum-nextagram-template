from app import app
from flask import Blueprint, render_template, request, url_for, flash, redirect
from models.user import User
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, current_user
import re
import boto3, botocore
from helpers import upload_file_to_s3, allowed_file
from config import S3_BUCKET




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
                flash('Login successfully!')
                # breakpoint()
                return render_template('home.html')
            else:
                flash('Wrong username or password')
                password_error = True
                return render_template('sessions/new.html', password_error = password_error)
        # else:
        #     flash('Wrong username or password')
        #     password_error = True
        #     return render_template('sessions/new.html', password_error = password_error)


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

@sessions_blueprint.route("/edit_password")
def edit_pw():
    return render_template('sessions/edit_pw.html')

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

@sessions_blueprint.route("/edit_pw", methods = ["POST"])
def edit_pw_form(): 
    old_password = request.form.get("old_password")
    check_password = request.form.get("check_old_password")
    new_password = request.form.get("new_password")
    if current_user.is_authenticated: 
        # if re.search("[A-Za-z0-9$&+,:;=?@#\"\\/|'<>.^*()%!-]", new_password) is None:
        if len(new_password) < 6:
            flash('Password has to at least 6 characters')
            password_error = True
            return render_template('sessions/edit_pw.html', password_error = password_error)
        elif re.search('[0-9]', new_password) is None:
            flash('Password must have at least 1 number!')
            password_error = True
            return render_template('sessions/edit_pw.html', password_error = password_error)
        elif re.search('[A-Z]', new_password) is None:
            flash('Password must have at least 1 capital letter!')
            password_error = True
            return render_template('sessions/edit_pw.html', password_error = password_error)
        elif re.search("[$&+,:;=?@#\"\\/|'<>.^*()%!-]", new_password) is None:
            flash('Password must have at least 1 special character!')
            password_error = True
            return render_template('sessions/edit_pw.html', password_error = password_error)
        else: 
            if old_password == check_password: 
                if check_password_hash(current_user.password, old_password):
                    query = User.update(password=generate_password_hash(new_password)).where(User.id == current_user.id)
                    if query.execute():
                        flash('Password changed!')
                        return redirect(url_for('home'))
                    else:
                        flash('Invalid password input')
                        return render_template('sessions/edit_pw.html')
                else:
                    flash('Incorrect Password')
                    password_error = True
                    return render_template('sessions/edit_pw.html', password_error = password_error)
            else: 
                flash('Password and retyped password are different')
                password_error = True
                return render_template('sessions/edit_pw.html', password_error = password_error)
    else: 
        flash('No user logged in')
        return render_template('sessions/edit_pw.html')

@sessions_blueprint.route('/upload')
def upload():
    return render_template('sessions/upload.html')

@sessions_blueprint.route('/upload_form', methods = ["POST"])
def upload_form():
    if "user_file" not in request.files:
        return flash('No user_file key in request.files')
    
    file = request.files["user_file"]

    if file.filename == "":
        return flash('Please select a file')

    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        # breakpoint()
        output = upload_file_to_s3(file, S3_BUCKET)
        return str(output)
    
    else: 
        return redirect(url_for('sessions.upload'))
        

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
 


