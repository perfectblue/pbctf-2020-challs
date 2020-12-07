import uuid
import os
import time
from flask import Flask, request, flash, redirect, send_from_directory, url_for

UPLOAD_FOLDER = '/tmp/notes'

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/notes/<filename>')
def note(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, mimetype="text/plain")


@app.route('/')
def index():
    if request.args.get('note') and len(request.args.get('note')) < 0x100:
        time.sleep(1)  # ddos protection
        filename = uuid.uuid4().hex
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "w") as f:
            f.write(request.args.get('note'))
        return redirect(url_for("note", filename=filename))
    return '''
        <!doctype html>
        <title>Create a note</title>
        <h1>Create a note</h1>
        <form>
        <textarea name=note></textarea>
        <input type=submit value=Upload>
        </form>
    '''
