from flask import Flask, render_template, request
import os
import boto3
from aws_helper import upload_file_to_audios
from pause_finder import pause_main
from general_helpers import convert_webm_to_wav

## Accessing .env file
from dotenv import load_dotenv

load_dotenv()
####

app = Flask(__name__)

# Ensure the upload directory exists
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    if file:
        print('FILE TYPE',type(file))
        # Save the file to the specified upload folder
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        if '.webm' in file_path:
            input_file = file_path
            output_file = file_path.replace('.webm', '.wav')
            
            file_path = output_file
            convert_webm_to_wav(input_file, output_file)

        ## Upload file to AWS S3
        upload_file_to_audios(file)

        ## Find Pauses
        pause_info, t = pause_main(file_path)
        print(pause_info)

        return 'File uploaded successfully!'

if __name__ == '__main__':
    app.run(debug=True)


## Add the 4P logic -> divide them into 4 APIs
## Add a speech transcription model hosted locally, to transcribe the speech.
## Once a model is zeroed down, experiment with its API on AWS Bedrock
## Add a Front-end logic to keep user engaged until the results get back
## Build a login layer (optional)