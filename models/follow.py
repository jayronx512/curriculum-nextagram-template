from models.base_model import BaseModel
import peewee as pw
from models.user import User
from models.images import Image
from playhouse.hybrid import hybrid_property

class Follow(BaseModel):
    follower = pw.ForeignKeyField(User, backref="followed")
    followed = pw.ForeignKeyField(User, backref="follower")

