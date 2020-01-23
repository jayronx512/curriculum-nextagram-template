import boto3, botocore
from config import S3_KEY, S3_SECRET, S3_BUCKET, S3_LOCATION
from app import app
from datetime import datetime

# breakpoint()
s3 = boto3.client(
   "s3",
   aws_access_key_id= S3_KEY,
   aws_secret_access_key= S3_SECRET
)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'jfif'}
def upload_file_to_s3(file, bucket_name, acl="public-read"):
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    try:

        s3.upload_fileobj(
            file,
            bucket_name,
            f"{timestamp}{file.filename}",
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e
    # return "{}{}".format(S3_LOCATION, f"{timestamp}{file.filename}")
    return f"{timestamp}{file.filename}"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS