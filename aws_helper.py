import boto3, os
from botocore.exceptions import BotoCoreError, ClientError
## Accessing .env file
from dotenv import load_dotenv

load_dotenv()
####

s3 = boto3.client('s3', aws_access_key_id= os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key= os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name='us-east-2')  # Specify your preferred region)

transcribe = boto3.client('transcribe', 
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name='us-east-2')

BUCKET_NAME = 'vd-experiments'
FOLDER_NAME = 'speech_ai/audios'

def upload_file_to_audios(fileobj, filename):
    
    print('Uploading to AWS!!!')
    s3_key = f'{FOLDER_NAME}/{filename}'

    s3.upload_fileobj(fileobj, BUCKET_NAME, s3_key)

    return None


def generate_presigned_url(s3_filename, expiration=3600*24*7):
    """
    Generate a presigned URL for an S3 object.
    
    :param s3_filename: The filename of the S3 object
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as a string
    """
    try:
        s3_key = f'{FOLDER_NAME}/{s3_filename}'
        response = s3.generate_presigned_url('get_object',
                                             Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
                                             ExpiresIn=expiration)

    
    except Exception as e:
        print(f'Error generating presigned URL: {e}')
        return None

    return response

def transcribe_audio(s3_filename, job_name, language_code='en-US'):
    """
    Transcribe an audio file from S3 using AWS Transcribe.
    
    :param s3_filename: The filename of the S3 object to transcribe
    :param job_name: A unique name for the transcription job
    :param language_code: The language code of the audio (default is 'en-US')
    :return: Job name if successfully started, None otherwise
    """
    try:
        s3_uri = f's3://{BUCKET_NAME}/{FOLDER_NAME.replace("audios", "transcriptions")}/{s3_filename}'
        
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_uri},
            MediaFormat=s3_filename.split('.')[-1],  # Assumes file extension is the format
            LanguageCode=language_code,
            OutputBucketName=BUCKET_NAME,
            OutputKey=f'{FOLDER_NAME}/transcriptions/{job_name}.json'
        )
        
        print(f"Transcription job '{job_name}' started successfully.")
        return job_name
    
    except (BotoCoreError, ClientError) as e:
        print(f"Error starting transcription job: {e}")
        return None


