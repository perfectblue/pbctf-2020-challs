from flask import Flask, request, session, jsonify, Response
import json
import redis
import random
import os
import time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tops3cr3t")

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',
)

HOST = os.environ.get("CHALL_HOST", "localhost:5000")

r = redis.Redis(host='redis')

@app.before_request
def session_init():
    if 'data_path' not in session:
        session['data_path'] = "/".join([hex(int(random.randint(0, 0xff)))[2:] for X in range(0x10)])
    if 'data' not in session:
        session['data'] = []
    pass

@app.after_request
def add_csp(response):
    response.headers['Content-Security-Policy'] = "default-src 'none'; script-src https://{host}/notes.js https://{host}/data/{}".format(session['data_path'], host=HOST)
    return response


@app.route('/data/<path:path>')
def data(path):
    if session['data_path'] == path:
        return Response("notes_callback(" + json.dumps(session['data']) + ")", mimetype="application/javascript")        
    return "Not authorized"

@app.route('/add', methods=['POST'])
def add():
    session['data'].append({"name":request.form['name'], "data":request.form['data']})
    session.modified = True
    return "Added succesfully"

@app.route("/do_report", methods=['POST'])
def do_report():
    cur_time = time.time()
    ip = request.headers.get('X-Forwarded-For').split(",")[-2].strip() #amazing google load balancer

    last_time = r.get('time.'+ip) 
    last_time = float(last_time) if last_time is not None else 0
    
    time_diff = cur_time - last_time

    if time_diff > 6:
        r.rpush('submissions', request.form['url'])
        r.setex('time.'+ip, 60, cur_time)
        return "submitted"

    return "rate limited"

@app.route('/notes')
def notes():
    return """
<body>
    <h1>NOTES</h1>
    <div id="notes">
    </div>
    <script src="/notes.js"></script>
    <script src="/data/{}" async defer></script>
</body>
    """.format(session['data_path'])

@app.route("/notes.js")
def js():
    return """
        function notes_callback(notes){
            notes.forEach(function(note){
                let name = note['name']
                let data = note['data']

                let name_node = document.createElement("h3");
                name_node.innerHTML = name;
                
                document.getElementById('notes').appendChild(name_node);

                let data_node = document.createElement("h5");
                data_node.innerHTML = data;

                document.getElementById('notes').appendChild(data_node);
                
            });
        }
    """

@app.route("/report", methods=['GET'])
def report():
    return """
<head>
    <title>Notes app</title>
</head>
<body>
    <h3><a href="/notes">List Notes</a>&nbsp;&nbsp;&nbsp;<a href="/">Add Note</a>&nbsp;&nbsp;&nbsp;<a href="/report">Report Link</a></h3>
        <hr>
        <h3>Please report suspicious URLs to admin</h3>
        <form action="/do_report" id="reportform" method=POST>
        URL: <input type="text" name="url" placeholder="URL">
        <br>
        <input type="submit" value="submit">
        </form>
    <br>
</body>
    """

@app.route('/')
def index():
    return """
<head>
    <title>Notes app</title>
</head>
<body>
    <h3><a href="/notes">List Notes</a>&nbsp;&nbsp;&nbsp;<a href="/">Add Note</a>&nbsp;&nbsp;&nbsp;<a href="/report">Report Link</a></h3>
        <hr>
        <h3> Add a note </h3>
        <form action="/add" id="noteform" method=POST>
        Name: <input type="text" name="name" placeholder="Note's name">
        <br>
        <textarea rows="10" cols="100" name="data" form="noteform" placeholder="Note's content"></textarea>
        <br>
        <input type="submit" value="submit">
        </form>
    <br>
</body>
    """

