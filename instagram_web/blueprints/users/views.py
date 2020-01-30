from app import app
from flask import Blueprint, render_template, request, url_for, flash, redirect
from models.user import User
from models.images import Image
from models.follow import Follow
from flask_wtf.csrf import CSRFProtect
from flask_login import login_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from instagram_web.util.helpers import upload_file_to_s3, allowed_file
from config import S3_BUCKET
import re, os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

now = datetime.now()
timestamp = datetime.timestamp(now)

csrf = CSRFProtect(app)

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')

@users_blueprint.route("/signup")
def signup():
    return render_template('users/new.html')

@users_blueprint.route("/signup_form", methods=["POST"])
def signup_form():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    retype_password = request.form.get('retype_password')
    # hashed_password = generate_password_hash(password)
    if password != retype_password:
        flash('Password and Retyped Password are different','warning')
        return render_template('users/new.html')
    new_user = User(username=username, email=email, password=password)
    
    if new_user.save():
        flash('New user created!', 'success')
        login_user(new_user)
        return redirect(url_for('home'))

    else:
        for err in new_user.errors:
            flash(err, 'danger')
            
    #     # flash(User.errors[0])
        return render_template('users/new.html', errors=new_user.errors)

@users_blueprint.route("/edit")
def edit():
    return render_template('users/edit.html')

@users_blueprint.route("/edit_email")
def edit_email():
    return render_template('users/edit_email.html')

@users_blueprint.route("/edit_password")
def edit_pw():
    return render_template('users/edit_pw.html')

@users_blueprint.route("/edit_form", methods = ["POST"])
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
                    flash('Username changed!', 'success')
                    return redirect(url_for('home'))

                else:
                    flash('Invalid username input', 'danger')
                    return render_template('users/edit.html')
            else:
                flash('Incorrect Password', 'danger')
                return render_template('users/edit.html')
        else: 
            flash('Password and retyped password are different', 'warning')
            return render_template('users/edit.html')

    else: 
        flash('No user logged in', 'danger')
        return render_template('users/edit.html')

@users_blueprint.route("/edit_email", methods = ["POST"])
def edit_email_form(): 
    new_email = request.form.get("new_email")
    check_password = request.form.get("check_password")
    check_retype_password = request.form.get("check_retype_password")
    if current_user.is_authenticated: 
        if re.search('[A-Za-z0-9._%+-]+@+[A-Za-z]+[.]+[c][o][m]', new_email) is not None:
            if check_password == check_retype_password: 
                if check_password_hash(current_user.password, check_password):
                    query = User.update(email=new_email).where(User.id == current_user.id)
                    duplicate_emails = User.get_or_none(email = new_email)
                    if duplicate_emails:
                        flash('Email has already been used!', 'danger')
                        return render_template('users/edit_email.html')
                    else:
                        query.execute()
                        flash('Email changed!', 'success')
                        return redirect(url_for('home'))
                        
                else:
                    flash('Incorrect Password', 'danger')
    
                    return render_template('users/edit_email.html')
            else: 
                flash('Password and retyped password are different', 'warning')

                return render_template('users/edit_email.html')
        else: 
            flash('Invalid email', 'danger')
            return render_template('users/edit_email.html')

    else: 
        flash('No user logged in', 'error')
        return render_template('users/edit_email.html')

@users_blueprint.route("/edit_pw", methods = ["POST"])
def edit_pw_form(): 
    old_password = request.form.get("old_password")
    check_password = request.form.get("check_old_password")
    new_password = request.form.get("new_password")
    if current_user.is_authenticated: 
        # if re.search("[A-Za-z0-9$&+,:;=?@#\"\\/|'<>.^*()%!-]", new_password) is None:
        if len(new_password) < 6:
            flash('Password has to at least 6 characters', 'warning')
            return render_template('users/edit_pw.html')
        elif re.search('[0-9]', new_password) is None:
            flash('Password must have at least 1 number!', 'warning')
            return render_template('users/edit_pw.html')
        elif re.search('[A-Z]', new_password) is None:
            flash('Password must have at least 1 capital letter!', 'warning')
            return render_template('users/edit_pw.html')
        elif re.search("[$&+,:;=?@#\"\\/|'<>.^*()%!-]", new_password) is None:
            flash('Password must have at least 1 special character!', 'warning')
            return render_template('users/edit_pw.html')
        else: 
            if old_password == check_password: 
                if check_password_hash(current_user.password, old_password):
                    query = User.update(password=generate_password_hash(new_password)).where(User.id == current_user.id)
                    if query.execute():
                        flash('Password changed!','success')
                        return redirect(url_for('home'))
                    else:
                        flash('Invalid password input','danger')
                        return render_template('users/edit_pw.html')
                else:
                    flash('Incorrect Password','danger')
                    return render_template('users/edit_pw.html')
            else: 
                flash('Password and retyped password are different','warning')
                return render_template('users/edit_pw.html')
    else: 
        flash('No user logged in','danger')
        return render_template('users/edit_pw.html')

@users_blueprint.route('/edit_profile_pic')
def edit_profile_pic():
    return render_template('users/edit_profile_pic.html')

@users_blueprint.route('/edit_profile_pic_form', methods = ["POST"])
def edit_profile_pic_form():
    if "user_file" not in request.files:
        flash('No user_file key in request.files','danger')
        return render_template('users/new.html')
    
    file = request.files["user_file"]

    if file.filename == "":
        return flash('Please select a file', 'danger')

    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        # breakpoint()
        output = upload_file_to_s3(file, S3_BUCKET)
        query = User.update(profile_pic = str(output)).where(User.id == current_user.id)
        if query.execute(): 
            return redirect(url_for('home'))
    
    else: 
        return redirect(url_for('users.edit_profile_pic'))


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


@users_blueprint.route('/', methods=['POST'])
def create():
    pass


@users_blueprint.route('/<username>', methods=["GET"])
def show(username): 
    # username = request.args.get('search_user')
    user = User.get_or_none(username = username)
    if current_user.is_authenticated: 
        if user is not None: 
            image = user.image
            user_follower = user.follower 
            user_followed = user.followed
            

            if user.username == current_user.username:
                # breakpoint()
                return render_template('users/profile.html', user = user, image = image, user_follower = user_follower, user_followed = user_followed)
            else: 
                # for i in user_follower:
                #     if i.follower_id == current_user.id:
                #         follower = User.get_or_none(username = current_user.username)
                #         breakpoint()
                #         return follower
                #     else:
                #         breakpoint()
                is_current_user_following = ""                
                if Follow.get_or_none(Follow.follower == current_user.id, Follow.followed == user.id):
                    is_current_user_following = True
                else:
                    is_current_user_following = False
    
            return render_template('users/profile.html', user = user, image = image, user_follower = user_follower, user_followed = user_followed, is_current_user_following = is_current_user_following)
        
        else: 
            flash('This user doesn\'t exist','danger')
            return render_template('users/user_existence.html', username=username)
    else: 
        flash('Please sign in to view profiles', 'danger')
        return render_template('users/profile.html')

@users_blueprint.route('/search', methods=["GET"])
def search():
    search = request.args.get("search_user")
    return redirect(url_for('users.show', username = search))

@users_blueprint.route('/upload', methods=["GET"])
def upload():
    return render_template('users/upload.html')

@users_blueprint.route('/upload_form', methods = ["POST"])
def upload_form():  
    if "user_file" not in request.files:
        flash('No user_file key in request.files','danger')
        return render_template('users/upload.html')
    
    file = request.files["user_file"]

    if file.filename == "":
        return flash('Please select a file', 'danger')

    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        # breakpoint()
        output = upload_file_to_s3(file, S3_BUCKET)
        new_image = Image(user_id = current_user.id, image_url = str(output))
        if new_image.save(): 
            # breakpoint()
            return redirect(url_for('users.upload'))

@users_blueprint.route('/privacy_form', methods=["POST"])
def privacy_form():
    user = User.get_by_id(current_user.id)
    if user.security == False:
        query = User.update(security = True).where(User.id == current_user.id) 
        query.execute()
        flash('Privacy changed to PRIVATE!','primary')
        return redirect(url_for('home'))
        
    else:
        query = User.update(security = False).where(User.id == current_user.id) 
        query.execute()
        flash('Privacy changed to PUBLIC', 'primary')
        return redirect(url_for('home'))

@users_blueprint.route('/follow/<username>', methods = ["POST"])
def follow(username):
    user = User.get_or_none(username = username)
    if user is not None: 
        followship = Follow(followed_id = user.id, follower_id = current_user.id)
        if followship.save():
            flash(f"You have successfully followed {user.username}!", 'success')
            return redirect(url_for('users.show', username = username))
        else: 
            flash("Follow failed!", 'danger')
            return render_template("users/profile.html")

@users_blueprint.route('/unfollow/<username>', methods = ["POST"])
def unfollow(username):
    user = User.get_or_none(username = username)
    if user is not None:
        unfollow = Follow.get_or_none(followed_id = user.id)
        if unfollow.delete_instance():
            flash(f"Successfully unfollowed {user.username}!", 'success')
            return redirect(url_for('users.show', username = username))

@users_blueprint.route('/follow/private/<username>', methods = ["POST"])
def follow_private(username):
    user = User.get_or_none(username = username)
    pending = False
    if user is not None: 
        if user.security == False:
            followship = Follow(followed_id = user.id, follower_id = current_user.id)
            if followship.save():
                flash(f"You have successfully followed {user.username}!", 'success')
                return redirect(url_for('users.show', username = username))
            else: 
                flash("Follow failed!", 'danger')
                return render_template("users/profile.html")

        else: 
            message = Mail(
            from_email= 'jj@gmail.com',
            to_emails= user.email,
            subject= f"Follow request from {current_user.username}",
            html_content= render_template("users/follow_request.html", user=user, timestamp = timestamp))

            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(str(e))

            flash(f"Follow request sent to {user.username}!", 'primary')
            pending = True
            # return redirect(url_for('users.show', username = user.username, pending = pending))
            return render_template('users/profile.html', user=user, pending = pending)
    else: 
        flash('LMAO', 'danger')
        return render_template('users/new.html')

@users_blueprint.route(f'/follow/public/<username>/{timestamp}', methods = ["GET"])
def follow_public(username):
    user = User.get_or_none(username = username)
    if user is not None: 
        followship = Follow(followed_id = user.id, follower_id = current_user.id)
        if followship.save():
            flash(f"You have successfully followed {user.username}!", 'success')
            return redirect(url_for('users.show', username = username))
        else: 
            flash("Follow failed!", 'danger')
            return render_template("users/profile.html")
   
    








# @users_blueprint.route('/', methods=["GET"])
# def index():
#     return "USERS"


# @users_blueprint.route('/<id>/edit', methods=['GET'])
# def edit(id):
#     pass


@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass
