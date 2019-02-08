import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from zipfile import ZipFile
from reps import FolderProcessor

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads/')
REPLAY_FOLDER = os.path.join(APP_ROOT, 'replays/')
REPLAYS_ZIP = 'Replays.zip'
ALLOWED_EXTENSIONS = set(['zip'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GNcC79NhRYEo7fIA3BQdKvlvIgRy'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def valid_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_replays(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with ZipFile(file_path, 'r') as zip:
        zip.printdir()
        zip.extractall(path=REPLAY_FOLDER)

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

    file_paths = get_all_file_paths('Replays/')

    with ZipFile(REPLAYS_ZIP, 'w') as zip: 
        # writing each file one by one 
        for file in file_paths:
            zip.write(file)

    os.chdir(APP_ROOT)

@app.route("/")
def home():
    return render_template("home.html")

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
            return redirect(url_for('replays_uploaded', filename=filename, sortop='m'))
        else:
            flash('please upload a .zip file of SC2 replays')
            return redirect(url_for('home'))

    return render_template("nofile.html")

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
            return redirect(url_for('replays_uploaded', filename=filename, sortop='p'))
        else:
            flash('please upload a .zip file of SC2 replays')
            return redirect(url_for('home'))

    return render_template("nofile.html")

@app.route("/replays/<sortop>/<filename>")
def replays_uploaded(sortop, filename):

    directory = filename[:-4]

    #unzip file to /replays/<filename w/o extension>
    extract_replays(filename)

    #run RepS
    target = os.path.join(REPLAY_FOLDER, directory)
    fp = FolderProcessor(target)
    fp.organize_replays(target, sortop)

    #zip /Replays
    zip_replays(directory)

    print(os.getcwd())

    #return the archived Replays
    return send_from_directory(target, REPLAYS_ZIP)

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/sort")
def sort():
    return render_template("sort.html")

if __name__ == "__main__":
    app.run(debug=True)