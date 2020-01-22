from app import app
from flask import Blueprint, render_template, request, url_for, flash, redirect
from models import user
from flask_wtf.csrf import CSRFProtect
from flask_login import login_user
from werkzeug.utils import secure_filename
from helpers import upload_file_to_s3, allowed_file
from config import S3_BUCKET


csrf = CSRFProtect(app)

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')

@users_blueprint.route("/signup")
def signup():
    return render_template('signup.html')

@users_blueprint.route("/signup_form", methods=["POST"])
def signup_form():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    retype_password = request.form.get('retype_password')
    # hashed_password = generate_password_hash(password)
    if password != retype_password:
        flash('Password and Retyped Password are different')
        password_error = True
        return render_template('signup.html', password_error = password_error)
    new_user = user.User(username=username, email=email, password=password)


    # while True: 
    #     if re.search('[A-Za-z0-9._%+-]+@+[A-Za-z]+[.]+[c][o][m]', email) is None:
    #         flash('Make sure your email is valid!')
    #         password_error = True
    #         return render_template('signup.html', password_error = password_error)
        
    #     else: 
    #         break
    # password = request.form.get('password')
    # retype_password = request.form.get('retype_password')
 

    # else: 
    #     while password == retype_password:
    #         if len(password) < 6:
    #             flash('Make sure your password is at least 6 letters')
    #             password_error = True
    #             return render_template('signup.html', password_error = password_error)
    #         elif re.search('[0-9]',password) is None:
    #             flash('Make sure your password has a number in it')
    #             password_error = True
    #             return render_template('signup.html', password_error = password_error)
    #         elif re.search('[A-Z]', password) is None:
    #             flash('Make sure your password has a capital letter in it')
    #             password_error = True
    #             return render_template('signup.html', password_error = password_error)
    #         elif re.search("[$&+,:;=?@#\"\\/|'<>.^*()%!-]", password) is None:
    #             flash('Make sure your password has special character in it')
    #             password_error = True
    #             return render_template('signup.html', password_error = password_error)
    #         else:
    #             hashed_password = generate_password_hash(password)
    #             new_user = user.User(username=username, email=email, password=hashed_password)
    #             break
    
    if new_user.save():
        flash('New user created!')
        login_user(new_user)
        return redirect(url_for('home'))

    else:
        for err in new_user.errors:
            flash(err)
            
    #     # flash(user.User.errors[0])
        return render_template('users/new.html', errors=new_user.errors)

@users_blueprint.route('/upload')
def upload():
    return render_template('users/upload.html')

@users_blueprint.route('/upload_form', methods = ["POST"])
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
        return redirect(url_for('users.upload'))


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


@users_blueprint.route('/', methods=['POST'])
def create():
    pass


@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    pass


@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"


@users_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    pass


@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass
