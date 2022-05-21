from paste.translogger import TransLogger
from waitress import serve
import configparser
import werkzeug
import helpers
import flask
import sys
import os

# os.environ["UPLOADS_DIR"] = "/media/veracrypt1/Edencloud/UniStuff/3.0 - CMP 3rd Year Project/Smarker/API/.uploads"

sys.path.insert(1, os.path.join("..", "Smarker"))
import database

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = ".uploads"
API_CONF = configparser.ConfigParser()
API_CONF.read("api.conf")


@app.route("/api/helloworld")
def helloworld():
    """GET ``/api/helloworld``

    Returns a friendly message to check the server is working
    """
    return flask.jsonify({"hello": "world!"})

@app.route("/api/mark", methods = ["post"])
def mark():
    """POST ``/api/mark``

    Expects to be a POST request of ``Content-Type: multipart/form-data``.

    * Expects a valid API key under the key ``key``

    * Expects an assessment name under the key ``assessment``

    * Expects a submission zip file under the key ``zip``

    * File dependences can be added with keys prefixed with ``filedep``, but a corrisponding key must also be present with the location of this file in the sandboxed environment: e.g. ``-F "filedep1=@../../aDependency.txt" -F "aDependency.txt=/aDependency.txt"``

    Returns a report in the JSON format.
    """
    # try:
    assessment_name = flask.request.form.get('assessment')
    api_key = flask.request.form.get('key')
    files = []

    with database.SmarkerDatabase(
        host = API_CONF.get("mysql", "host"), 
        user = API_CONF.get("mysql", "user"), 
        passwd = API_CONF.get("mysql", "passwd"), 
        db = "Smarker",
        port = API_CONF.getint("mysql", "port")) as db:

        if db.valid_apikey(api_key):
            f = flask.request.files["zip"]
            zip_name = f.filename
            f.save(os.path.join(".uploads/", f.filename))
            # even though this is inside docker, we are accessing the HOST docker daemon
            # so we have to pass through the HOST location for volumes... very annoying I know
            # so we set this environment variable
            #       https://serverfault.com/questions/819369/mounting-a-volume-with-docker-in-docker
            files.append("%s:/tmp/%s" % (os.path.join(os.environ["UPLOADS_DIR"], zip_name), zip_name))
   
            for file_dep in flask.request.files.keys():
                if file_dep.startswith("filedep"):
                    f = flask.request.files[file_dep]
                    f.save(os.path.join(".uploads/", f.filename))
                    dep_name = os.path.split(f.filename)[-1]
                    client_loc = flask.request.form.get(dep_name)
                    if client_loc is None:
                        return flask.abort(flask.Response("You need to specify a location to put file dependency '%s' e.g.  '%s=/%s'" % (dep_name, dep_name, dep_name), status=500))
                    
                    files.append("%s:%s" % (os.path.join(os.environ["UPLOADS_DIR"], dep_name), client_loc))
            
            
            try:
                return flask.jsonify(helpers.run_smarker_simple(db, zip_name, assessment_name, files))
            except Exception as e:
                flask.abort(flask.Response(str(e), status=500))
        else:
            flask.abort(403)
    # except (KeyError, TypeError, ValueError):
    #     flask.abort(400)


if __name__ == "__main__":
    try:
        if sys.argv[1] == "--production":
            serve(
                TransLogger(app), 
                host = API_CONF.get("production", "host"), 
                port = API_CONF.getint("production", "port"), 
                threads = 32
            )
        else:
            app.run(
                host = API_CONF.get("testing", "host"), 
                port = API_CONF.getint("testing", "port"), 
                debug = True
            )
    except IndexError:
        app.run(
            host = API_CONF.get("testing", "host"), 
            port = API_CONF.getint("testing", "port"), 
            debug = True
        )