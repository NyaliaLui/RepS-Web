import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from reps import Dispatcher
import logging
import sys
import boto3
from botocore.client import Config
import botocore
import json

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_MANAGER = Dispatcher(APP_ROOT)
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
REPLAY_FOLDER = os.path.join(APP_ROOT, 'replays')
ARCHIVE_FOLDER = os.path.join(APP_ROOT, 'archive')
ALLOWED_EXTENSIONS = set(['zip', 'rar'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GNcC79NhRYEo7fIA3BQdKvlvIgRy'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

def valid_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def setup_app():
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

    return app

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

    S3_BUCKET = os.environ.get("S3_BUCKET")
    s3 = boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))

    try:
        s3.download_file(S3_BUCKET, archive_name, archive_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print(archive_name + " does not exist.")
        else:
            raise
    except TypeError as ex:
        print(S3_BUCKET, type(S3_BUCKET))
        print(archive_name, type(archive_name))
        raise ex

    os.chdir(APP_ROOT)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if ('perm' not in request.form) or (request.form['perm'] != 'yes'):
            return json.dumps({'msg':'permission to store archive is required'}), 500

        if 'replays' not in request.files:
            return json.dumps({'msg':'No archive uploaded'}), 500
        
        replays = request.files['replays']
        if replays.filename == '':
            return json.dumps({'msg':'the archive needs a filename'}), 500

        if replays and valid_file(replays.filename):
            filename = secure_filename(replays.filename)
            replays.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return json.dumps({'msg':'success'}), 200
        else:
            return json.dumps({'msg':'please upload a .zip or .rar file of SC2 replays'}), 500
    
    return render_template("nofile.html")

@app.route("/sort/player", methods=['GET', 'POST'])
def org_player():
    if request.method == 'POST':
    
        archivename = request.form['archivename']
        rename_enabled = True
        #rename disabled if it wasn't set (non exists)
        try:
            request.form['rename']
        except:
            rename_enabled = False

        filename = secure_filename(archivename)
        name = ''
        ext = filename[-4:]
        try:
            name = ARCHIVE_MANAGER.dispatch(filename, 'p', rename_enabled)
        except Exception:
            flash('something went wrong. make sure the archive doesn\'t have a folder named Replays')
            return redirect(url_for('home'))

        return redirect(url_for('thankyou', directory=name, extension=ext))

    return render_template("nofile.html")

@app.route("/sort/matchup", methods=['GET', 'POST'])
def org_matchup():
    if request.method == 'POST':
    
        archivename = request.form['archivename']
        rename_enabled = True
        #rename disabled if it wasn't set (non exists)
        try:
            request.form['rename']
        except:
            rename_enabled = False

        filename = secure_filename(archivename)
        name = ''
        ext = filename[-4:]
        try:
            name = ARCHIVE_MANAGER.dispatch(filename, 'm', rename_enabled)
        except Exception:
            flash('something went wrong. make sure the archive doesn\'t have a folder named Replays')
            return redirect(url_for('home'))

        return redirect(url_for('thankyou', directory=name, extension=ext))

    return render_template("nofile.html")
    
@app.route("/replays/<directory>/<extension>/Replays")
def download(directory, extension):

    location = os.path.join(REPLAY_FOLDER, directory)

    if extension == '.zip':
        return send_from_directory(location, 'Replays.zip')
    elif extension == '.rar':
        return send_from_directory(location, 'Replays.rar')

@app.route("/thankyou/<directory>/<extension>")
def thankyou(directory, extension):
    return render_template("thankyou.html", result=directory, filetype=extension)

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
    app = setup_app()

    app.run(host='0.0.0.0', port=5015, debug=True)
