import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from zipfile import ZipFile
from reps import FolderProcessor
from FileRenamer import FileRenamer
from shutil import move
import logging
import sys
import json, boto3
from botocore.client import Config

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, os.path.join('tmp', 'uploads'))
REPLAY_FOLDER = os.path.join(APP_ROOT, os.path.join('tmp', 'replays'))
REPLAYS_ZIP = 'Replays.zip'
RENAMER = FileRenamer()
ALLOWED_EXTENSIONS = set(['zip'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GNcC79NhRYEo7fIA3BQdKvlvIgRy'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

def valid_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_replays(src, dest):
    file_path = os.path.join(UPLOAD_FOLDER, src)
    target_path = os.path.join(REPLAY_FOLDER, dest)

    with ZipFile(file_path, 'r') as zip:
        zip.extractall(path=target_path)

def get_all_file_paths(directory): 
  
    file_paths = [] 
  
    for root, directories, files in os.walk(directory): 
        for filename in files: 
            filepath = os.path.join(root, filename) 
            file_paths.append(filepath) 
  
    return file_paths 

def zip_replays(dirname):
    dir_path = os.path.join(REPLAY_FOLDER, dirname)
    os.chdir(dir_path)

    file_paths = get_all_file_paths('Replays')

    with ZipFile(REPLAYS_ZIP, 'w') as zip: 
        # writing each file one by one 
        for file in file_paths:
            zip.write(file)

    os.chdir(APP_ROOT)

def replays_uploaded(filename, sortop):

    directory = filename[:-4]

    #unzip file to /replays/<filename w/o extension>
    extract_replays(src=filename, dest=directory)

    #run RepS
    target = os.path.join(REPLAY_FOLDER, directory)
    fp = FolderProcessor(target)
    fp.organize_replays(target, sortop)

    #zip /Replays
    zip_replays(directory)

    #rename files for archival purposes
    name = RENAMER.next_available_name()
    olddir = target
    newdir = os.path.join(REPLAY_FOLDER, name)
    move(olddir, newdir)

    oldzip = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    newzip = os.path.join(app.config['UPLOAD_FOLDER'], name+'.zip')
    move(oldzip, newzip)

    #return the directory where sorted replays were uploaded
    return name

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
                name = replays_uploaded(filename, 'p')
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
                name = replays_uploaded(filename, 'm')
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

@app.route('/sign_s3/')
def sign_s3():
  S3_BUCKET = os.environ.get('S3_BUCKET')

  file_name = request.args.get('file_name')
  file_type = request.args.get('file_type')

  s3 = boto3.client('s3', config = Config(signature_version = 's3v4'))

  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    Fields = {"acl": "public-read", "Content-Type": file_type},
    Conditions = [
      {"acl": "public-read"},
      {"Content-Type": file_type}
    ]
  )

  return json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
  })

if __name__ == "__main__":
    try:
        os.mkdir(UPLOAD_FOLDER)
    except:
        print('uploads already exists')

    try:
        os.mkdir(REPLAY_FOLDER)
    except:
        print('replays already exists')

    app.run(debug=True)