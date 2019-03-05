import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
import logging
import sys
import boto3
from botocore.client import Config
import botocore

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, os.path.join('tmp', 'uploads'))
REPLAY_FOLDER = os.path.join(APP_ROOT, os.path.join('tmp', 'replays'))
ARCHIVE_FOLDER = os.path.join(APP_ROOT, os.path.join('tmp', 'archive'))
REPLAYS_ZIP = 'Replays.zip'
ALLOWED_EXTENSIONS = set(['zip'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GNcC79NhRYEo7fIA3BQdKvlvIgRy'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

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

    S3_BUCKET = os.environ.get('S3_BUCKET')
    s3 = boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))

    try:
        s3.download_file(S3_BUCKET, archive_name, archive_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print(archive_name + " does not exist on S3.")
        else:
            raise

    os.chdir(APP_ROOT)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/premade")
def premade():
    return render_template("premade.html")

@app.route("/archive/<directory>/<sortop>/Replays", methods=['GET', 'POST'])
def download(directory, sortop):

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

    app.run(debug=True)