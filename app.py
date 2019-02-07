import os
from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = set(['zip'])
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/org/matchup", methods=['GET', 'POST'])
def org_matchup():
    if request.method == 'POST':
    
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('replays_uploaded', filename=filename))

    return render_template("nofile.html")

@app.route("/org/player", methods=['GET', 'POST'])
def org_player():
    if request.method == 'POST':
    
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('replays_uploaded', filename=filename))

    return render_template("nofile.html")

@app.route("/replays"):
def replays_uploaded(filename):

    #run RepS here

    #return the archived Replays
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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