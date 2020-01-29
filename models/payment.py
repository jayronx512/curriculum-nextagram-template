from models.base_model import BaseModel
import peewee as pw
from models.user import User
from models.images import Image
from playhouse.hybrid import hybrid_property

class Payment(BaseModel):
    donator = pw.ForeignKeyField(User, backref = 'donation')
    image = pw.ForeignKeyField(Image, backref = 'donation')
    payment = pw.IntegerField(default = 5)
    message = pw.TextField(null=True)





