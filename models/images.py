from models.base_model import BaseModel
import peewee as pw
from models.user import User
from config import S3_LOCATION
from playhouse.hybrid import hybrid_property

class Image(BaseModel):
    user = pw.ForeignKeyField(User, backref = 'image')
    image_url = pw.TextField(null=True)

    @hybrid_property
    def image_path(self):
        return S3_LOCATION + self.image_url


