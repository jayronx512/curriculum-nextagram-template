from models.base_model import BaseModel
import peewee as pw
import re
from werkzeug.security import generate_password_hash
from flask_login import UserMixin
from urllib.parse import urlparse
from playhouse.hybrid import hybrid_property
from config import S3_LOCATION

class User(BaseModel, UserMixin):
    username = pw.CharField(unique=True)
    email = pw.CharField(unique=True)
    password = pw.CharField(unique=False)
    description = pw.CharField(default="Welcome to my space!")
    profile_pic = pw.TextField(null=True)
    security = pw.BooleanField(default=False)

    def validate(self):
        duplicate_emails = User.get_or_none(User.email == self.email)
        if duplicate_emails:
            self.errors.append('Email has been used')

        duplicate_user = User.get_or_none(User.username == self.username)
        if duplicate_user: 
            self.errors.append('Username has been used')
        
        if re.search('[A-Za-z0-9._%+-]+@+[A-Za-z]+[.]+[c][o][m]', self.email) is None:
            self.errors.append('Invalid email')
        if len(self.password) < 6:
            self.errors.append('Password has to be at least 6 characters!')
        elif re.search('[0-9]', self.password) is None:
            self.errors.append('Password must have at least 1 number!')
        elif re.search('[A-Z]', self.password) is None:
            self.errors.append('Password must have at least 1 capital letter!')
        elif re.search("[$&+,:;=?@#\"\\/|'<>.^*()%!-]", self.password) is None:
            self.errors.append('Password must have at least 1 special character!')

        self.password = generate_password_hash(self.password)

    def followers(self):
        return ([i.follower for i in self.follower])

    def followings(self):
        return ([i.followed for i in self.followed])

    

    

    @hybrid_property
    def image_path(self):
        if self.profile_pic:
            return S3_LOCATION + self.profile_pic
        else: 
            return "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSo_HDyoYqHSQ5jx4uhfKVv86BKFo6ZBTyRxYAYdu3J8DHb_t6g&s"

    # @hybrid_property
    # def image_domain(self):
    #     return urlparse(self.profile_pic).scheme +"://" + urlparse(self.profile_pic).netloc

    # @hybrid_property
    # def profile_image_url(self):
    #     return self.image_domain  + self.image_path

        # if User.password == User.retype_password:
        #     self.errors.append('Password and retyped password different')


