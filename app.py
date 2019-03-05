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
ARCHIVE_FOLDER = os.path.join(APP_ROOT, 'tmp', 'archive')
REPLAYS_ZIP = 'Replays.zip'
ALLOWED_EXTENSIONS = set(['zip'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GNcC79NhRYEo7fIA3BQdKvlvIgRy'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

def create_subfolders(directory):
    os.chdir(ARCHIVE_FOLDER)
    os.mkdir(directory)
    os.mkdir(os.path.join(directory, 'M'))
    os.mkdir(os.path.join(directory, 'P'))
    os.chdir(APP_ROOT)

def transfer_from_s3(archive_name, directory, sortop):
    os.chdir(ARCHIVE_FOLDER)

    S3_BUCKET = os.environ.get('S3_BUCKET')
    s3 = boto3.resource('s3')
    local_dest = os.path.join(directory, sortop, archive_name)

    try:
        s3.Bucket(S3_BUCKET).download_file(archive_name, local_dest)
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

        return send_from_directory(location, zip_file)

    return render_template("nofile.html")

if __name__ == "__main__":
    try:
        os.mkdir(ARCHIVE_FOLDER)
    except:
        print('archive already exists')
        
    directory = 'IEM-Katowice-2019'
    create_subfolders('IEM-Katowice-2019')
    transfer_from_s3('IEM-Katowice-2019-SBP.zip', directory, 'P')
    transfer_from_s3('IEM-Katowice-2019-SBM.zip', directory, 'M')
    print('archives successfully transfered')

    try:
        os.mkdir(UPLOAD_FOLDER)
    except:
        print('uploads already exists')

    try:
        os.mkdir(REPLAY_FOLDER)
    except:
        print('replays already exists')

    app.run(debug=True)