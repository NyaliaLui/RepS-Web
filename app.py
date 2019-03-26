import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from reps import Dispatcher
import logging
import sys
import boto3
from botocore.client import Config
import botocore

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_MANAGER = Dispatcher(APP_ROOT)
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
REPLAY_FOLDER = os.path.join(APP_ROOT, 'replays')
ARCHIVE_FOLDER = os.path.join(APP_ROOT, 'archive')
REPLAYS_ZIP = 'Replays.zip'
ALLOWED_EXTENSIONS = set(['zip'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GNcC79NhRYEo7fIA3BQdKvlvIgRy'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

def valid_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_subfolders(directory):
    os.chdir(ARCHIVE_FOLDER)

    try:
        os.mkdir(directory)
    except OSError:
        print(directory + ' already created')

    try:
        os.mkdir(os.path.join(directory, 'M'))
    except OSError:
        print(directory + '/M already created')

    try:
        os.mkdir(os.path.join(directory, 'P'))
    except OSError:
        print(directory + '/P already created')

    os.chdir(APP_ROOT)

def transfer_from_s3(archive_name, local_dest):
    os.chdir(local_dest)

    S3_BUCKET = os.getenv('S3_BUCKET')
    s3 = boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))

    try:
        s3.download_file(S3_BUCKET, archive_name, archive_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print(archive_name + " does not exist on S3.")
        else:
            raise
    except TypeError as ex:
        print(S3_BUCKET, type(S3_BUCKET))
        print(archive_name, type(archive_name))

    os.chdir(APP_ROOT)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/sort/player", methods=['GET', 'POST'])
def org_player():
    if request.method == 'POST':
    
        if 'replays' not in request.files:
            flash('No .zip file uploaded')
            return redirect(url_for('home'))
        
        replays = request.files['replays']
        if replays.filename == '':
            flash('the .zip file needs a filename')
            return redirect(url_for('home'))

        if replays and valid_file(replays.filename):
            filename = secure_filename(replays.filename)
            replays.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            name = ''
            try:
                name = ARCHIVE_MANAGER.dispatch(filename, 'p')
            except Exception:
                flash('something went wrong. make sure the zip archive doesn\'t have a folder named Replays')
                return redirect(url_for('home'))

            return redirect(url_for('thankyou', directory=name))
        else:
            flash('please upload a .zip file of SC2 replays')
            return redirect(url_for('home'))

    return render_template("nofile.html")

@app.route("/sort/matchup", methods=['GET', 'POST'])
def org_matchup():
    if request.method == 'POST':
    
        if 'replays' not in request.files:
            flash('No .zip file uploaded')
            return redirect(url_for('home'))
        
        replays = request.files['replays']
        if replays.filename == '':
            flash('the .zip file needs a filename')
            return redirect(url_for('home'))

        if replays and valid_file(replays.filename):
            filename = secure_filename(replays.filename)
            replays.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            name = ''
            try:
                name = ARCHIVE_MANAGER.dispatch(filename, 'm')
            except Exception:
                flash('something went wrong. make sure the zip archive doesn\'t have a folder named Replays')
                return redirect(url_for('home'))

            return redirect(url_for('thankyou', directory=name))
        else:
            flash('please upload a .zip file of SC2 replays')
            return redirect(url_for('home'))

    return render_template("nofile.html")
    
@app.route("/replays/<directory>/Replays")
def download(directory):

    location = os.path.join(REPLAY_FOLDER, directory)

    return send_from_directory(location, REPLAYS_ZIP)

@app.route("/thankyou/<directory>")
def thankyou(directory):
    return render_template("thankyou.html", result=directory)

@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/premade")
def premade():
    return render_template("premade.html")

@app.route("/archive/<directory>/<sortop>/Replays", methods=['GET', 'POST'])
def send_archive(directory, sortop):

    if request.method == 'GET':
        location = os.path.join(ARCHIVE_FOLDER, directory, sortop)
        zip_file = directory + '-' + 'SB' + sortop + '.zip'

        if not os.path.isfile(os.path.join(location, zip_file)):
            create_subfolders(directory)
            transfer_from_s3(zip_file, location)
            print('archives successfully transfered')

        return send_from_directory(location, zip_file)

    return render_template("nofile.html")

if __name__ == "__main__":
    try:
        os.mkdir(ARCHIVE_FOLDER)
    except:
        print('archive already exists')
    
    try:
        os.mkdir(UPLOAD_FOLDER)
    except:
        print('uploads already exists')

    try:
        os.mkdir(REPLAY_FOLDER)
    except:
        print('replays already exists')

    app.run(host='0.0.0.0', port=80, debug=True)