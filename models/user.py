from models.base_model import BaseModel
import peewee as pw
import re
from werkzeug.security import generate_password_hash
from flask_login import UserMixin

class User(BaseModel, UserMixin):
    username = pw.CharField(unique=False)
    email = pw.CharField(unique=True)
    password = pw.CharField(unique=False)
    profile_pic = pw.TextField(null=True)

    def validate(self):
        duplicate_emails = User.get_or_none(User.email == self.email)
        if duplicate_emails:
            self.errors.append('Email has been used')
        
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


        # if User.password == User.retype_password:
        #     self.errors.append('Password and retyped password different')


