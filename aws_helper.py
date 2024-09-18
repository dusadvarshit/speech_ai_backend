import boto3, os

## Accessing .env file
from dotenv import load_dotenv

load_dotenv()
####

s3 = boto3.client('s3', aws_access_key_id= os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key= os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name='us-east-2')  # Specify your preferred region)

BUCKET_NAME = 'vd-experiments'

def upload_file_to_audios(fileobj):
    FOLDER_NAME = 'speech_ai/audios'
    print('Uploading to AWS!!!')
    s3_key = f'{FOLDER_NAME}/{fileobj.filename}'

    s3.upload_fileobj(fileobj, BUCKET_NAME, s3_key)

    return None
