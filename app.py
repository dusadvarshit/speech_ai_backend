from flask import Flask, render_template, request, Response, jsonify
from flask_cors import CORS
import os
import boto3
from aws_helper import upload_file_to_audios, generate_presigned_url, transcribe_audio, run_generic_lambda
from pause_finder import pause_main, pause_feedback, pause_score
from pitch_finder import return_pitch_score, pitch_feedback
from pace_finder import compute_articulation_rate, pace_feedback
from power_finder import return_energy_score, energy_feedback
from general_helpers import convert_webm_to_wav
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from datetime import datetime, timedelta
import uuid
import requests

## Accessing .env file
from dotenv import load_dotenv

load_dotenv()
####

app = Flask(__name__)
# Allow requests from the React app
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://speechai.blackboardradio.com"]}})

# Configure PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=6)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=True)
    recordings = db.relationship('Recording', backref='user', lazy=True)
    
class Recording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    file_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    s3_presigned_url = db.Column(db.String(2048), nullable=True)
    audio_signal_analysis = db.Column(db.JSON, nullable=True)
    audio_signal_feedback = db.Column(db.JSON, nullable=True)

# Ensure the upload directory exists
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    name = data.get('name')

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password,
                    email=email, name=name)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print('DAAATAA',data)
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 402

@app.route('/')
# @jwt_required()
def index():
    return render_template('index.html'), 201

@app.route('/hello')
def hello():
    return Response("{'hello':'hello'}", status=201, mimetype='application/json')

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload():
    print('Uploading...', request.files['file'].filename)
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']

    current_user = User.query.filter_by(username=get_jwt_identity()).first()
    print('Current User',current_user.username)

    new_recording = Recording(
            user_id=current_user.id,
            file_name=file.filename,
            unique_id=str(uuid.uuid4())
        )

    s3_filename = new_recording.unique_id + '.wav'
    try:
        ## Upload file to AWS S3
        upload_file_to_audios(file, s3_filename)
        url = generate_presigned_url(s3_filename)

        new_recording.s3_presigned_url = url
        db.session.add(new_recording)
        db.session.commit()
        print('DB commit successful')

        run_generic_lambda('4P_analysis', payload= json.dumps(
            {'s3_urls': [url]}
        ))
        transcribe_audio(s3_filename, job_name=new_recording.unique_id, language_code='en-US')

        return 'File uploaded successfully!', 201
    
    except Exception as e:
        print('Error in adding recording to DB',e)
    

@app.route('/list')
@jwt_required()
def list():
    current_user = User.query.filter_by(username=get_jwt_identity()).first()
    print(request.args)

    page = request.args.get('page', 1, type=int)  # Default to page 1
    per_page = request.args.get('per_page', 10, type=int)  # Default to 10 items per page
    print('PAGE', page)
    
    # Query the database with LIMIT and OFFSET
    recordings = Recording.query.options(load_only(Recording.file_name, Recording.s3_presigned_url, Recording.audio_signal_feedback)).filter_by(user_id=current_user.id).order_by(Recording.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    file_list = []

    for file in recordings: 
        current_dict = {"filename": file.file_name, "url": file.s3_presigned_url}
 
        current_dict['pause_feedback'] = file.audio_signal_feedback['pause_feedback']
        current_dict['pitch_feedback'] = file.audio_signal_feedback['pitch_feedback']
        current_dict['energy_feedback'] = file.audio_signal_feedback['energy_feedback']
        current_dict['pace_feedback'] = file.audio_signal_feedback['pace_feedback']
        
        file_list.append(current_dict)

    return jsonify({'data': file_list, 
        'total': recordings.total,  
        'pages': recordings.pages,  
        'current_page': recordings.page,
        'next_page': recordings.next_num,
        'prev_page': recordings.prev_num 
        }), 201

@app.route('/identity')
@jwt_required()
def identity():
    user_id = get_jwt_identity()

    return jsonify({'user_id': user_id}), 201


@app.route('/generate_presigned_url_all', methods=['GET'])
@jwt_required()
def generate_presigned_url_all():
    
    user = User.query.filter_by(username=get_jwt_identity()).first()
    missing_urls_recordings = Recording.query.options(load_only(Recording.unique_id, Recording.s3_presigned_url)).all()#.filter_by(user_id = user.id).filter_by(s3_presigned_url =  None).all()

    for recording in missing_urls_recordings:
        s3_filename = recording.unique_id + '.wav'
        url = generate_presigned_url(s3_filename)
        recording.s3_presigned_url = url

    db.session.commit()

    return 'Generated presigned urls successfully!', 201

@app.route('/generate_audio_signal_analysis', methods=['GET'])
@jwt_required()
def generate_audio_signal_analysis():
    
    missing_signal_recordings = Recording.query.options(load_only(Recording.s3_presigned_url)).filter_by(audio_signal_analysis =  None) # .all() #
    s3_urls = [i.s3_presigned_url for i in missing_signal_recordings]

    payload = json.dumps({
    "s3_urls": s3_urls
    })

    run_generic_lambda('4P_analysis', payload)

    return 'Started a lambda function to perform audio signal analysis successfully!', 201 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)


## Add the 4P logic -> divide them into 4 APIs
## Add a speech transcription model hosted locally, to transcribe the speech.
## Once a model is zeroed down, experiment with its API on AWS Bedrock
## Add a Front-end logic to keep user engaged until the results get back
## Build a login layer (optional)