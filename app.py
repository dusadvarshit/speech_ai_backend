from flask import Flask, render_template, request, Response, jsonify
from flask_cors import CORS
import os
import boto3
from aws_helper import upload_file_to_audios
from pause_finder import pause_main
from general_helpers import convert_webm_to_wav
import json
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate

## Accessing .env file
from dotenv import load_dotenv

load_dotenv()
####

app = Flask(__name__)
# Allow requests from the React app
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Configure PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

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
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/')
@jwt_required()
def index():
    return render_template('index.html')

@app.route('/hello')
@jwt_required()
def hello():
    return Response("{'hello':'hello'}", status=201, mimetype='application/json')

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload():
    print(request)
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
        # upload_file_to_audios(file)

        ## Find Pauses
        pause_info, t = pause_main(file_path)
        print(pause_info)

        return 'File uploaded successfully!'

@app.route('/list', methods=['get'])
@jwt_required()
def list():
    file_list = os.listdir("./uploads")

    return {'data': file_list}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)


## Add the 4P logic -> divide them into 4 APIs
## Add a speech transcription model hosted locally, to transcribe the speech.
## Once a model is zeroed down, experiment with its API on AWS Bedrock
## Add a Front-end logic to keep user engaged until the results get back
## Build a login layer (optional)