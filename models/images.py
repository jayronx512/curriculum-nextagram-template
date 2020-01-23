from models.base_model import BaseModel
import peewee as pw
from models.user import User

class Image(BaseModel):
    user = pw.ForeignKeyField(User, backref = 'image')
    image_url = pw.TextField(null=True)


