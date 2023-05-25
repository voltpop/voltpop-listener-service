import argparse
import codecs
import datetime
import flask
import hashlib
import hmac
import json
import os
import pickle
import redis
import yaml
import sqlite3
import pprint

pp = pprint.PrettyPrinter()

class Announcer():
    def __init__(self):
        # Init / Configure the Flask app
        template_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "app/templates")
        static_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "app/static")
        self.toolbar=open(os.path.join(template_path, "toolbar.html"), "r").read()
        self.announcer = app = flask.Flask(__name__, 
                static_folder=static_path,
                template_folder=template_path,
                )
        # PubSub configuration
        self.r = redis.StrictRedis(os.environ['VPA_REDIS_HOST'], os.environ['VPA_REDIS_MAP_PORT'], charset="utf8", decode_responses=True, socket_keepalive=True, socket_timeout=300)
        self.p = self.r.pubsub()
        self.dbfile = config["dbfile"]

        # Initialize the Announcement Stash
        db_con = sqlite3.connect(self.dbfile)
        db = db_con.cursor()
        db.execute("""CREATE TABLE IF NOT EXISTS main.channels (
            id INTEGER PRIMARY KEY,
            key TEXT NOT NULL,
            security BOOL NOT NULL,
            enabled BOOL NOT NULL,
            queryable BOOL NOT NULL);""")

        db.execute("""CREATE TABLE IF NOT EXISTS main.data (
            id INTEGER PRIMARY KEY,
            datetime TEXT NOT NULL,
            key TEXT NOT NULL,
            payload BLOB NOT NULL);""")
        db_con.commit()
        db_con.close()
        
        @app.route('/', methods=["GET"])
        def index():
            channels = self.fetchChannels()
            return flask.render_template('index.html', toolbar=self.toolbar, channels=channels)

        @app.route('/add_channel', methods=["GET", "POST"])
        def add_channel():
            channels = [ channel[1] for channel in self.fetchChannels() ]
            if flask.request.method == "POST":
                # Collect Channel details from the form
                values = [ flask.request.form.get("key") ]
                if flask.request.form.get("security"): values.append(True)
                else: values.append(False)

                if flask.request.form.get("enabled"): values.append(True)
                else: values.append(False)

                if flask.request.form.get("queryable"): values.append(True)
                else: values.append(False)

                if values[0] in channels:
                    error_msg = "%s is already a channel" % (values[0])
                    return flask.render_template('add_channel.html', toolbar=self.toolbar, error_msg=error_msg)
                else:
                    error_msg = "Added %s!" % (values[0])
                    self.addChannel(values)
                    return flask.render_template('add_channel.html', toolbar=self.toolbar, error_msg=error_msg)
            return flask.render_template('add_channel.html', toolbar=self.toolbar, error_msg="")

        @app.route('/query_channel', methods=["GET", "POST"])
        def query_channel():
            channels = self.fetchChannels()
            q_reference = {}
            for channel in channels:
                q_reference[channel[1]] = {
                        "security": channel[2],
                        "enabled": channel[3],
                        "queryable": channel[4],
                        }
            data = "{}"
            if flask.request.method == "POST": 
                key = flask.request.form.get("key")
                if key != "Channel Key" and q_reference[key]["queryable"]:
                    data = self.queryAnnouncement(key)
            channels = [ key[1] for key in self.fetchChannels() ]
            return flask.render_template('query_channel.html', toolbar=self.toolbar, channels=channels, data=json.loads(data))

        @app.route('/query/<key>', methods=["GET"])
        def query_example(key):
            channels = self.fetchChannels()
            q_reference = {}
            for channel in channels:
                q_reference[channel[1]] = {
                        "security": channel[2],
                        "enabled": channel[3],
                        "queryable": channel[4],
                        }
            if key in q_reference.keys() and q_reference[key]["queryable"]:
                return '''{}'''.format(self.queryAnnouncement(key))
            else:
                flask.abort(403)
            #query = flask.request.args.get('query')

        @app.route('/new_announcement', methods=['GET', 'POST'])
        def new_announcement():
            status = ""
            channels = self.fetchChannels()
            q_reference = {}
            for channel in channels:
                q_reference[channel[1]] = {
                        "security": channel[2],
                        "enabled": channel[3],
                        "queryable": channel[4],
                        }

            data = "{}"
            if flask.request.method == "POST":
                key = flask.request.form.get("key")
                data = flask.request.form.get("data")
                q = q_reference[key]
                if key != "Channel Key" and q["enabled"]:
                    if not q['security']:
                        self.stashAnnouncement([datetime.datetime.now().isoformat(), key, str(data)])
                        self.r.publish(key, codecs.encode(pickle.dumps(data, 0), 'base64'))
                        status = "Message Sent!"
            return flask.render_template('new_announcement.html', toolbar=self.toolbar, channels=q_reference.keys(), status=status)

        @app.route('/announce/<key>', methods=['POST'])
        def voltpop_announcement(key):
            channels = self.fetchChannels()
            q_reference = {}
            for channel in channels:
                q_reference[channel[1]] = {
                        "security": channel[2],
                        "enabled": channel[3],
                        "queryable": channel[4],
                        }
            if key in q_reference.keys() and q_reference[key]["enabled"]:
                q = q_reference[key]
                # Security!!!
#                if q['security'] and q['secure_token'] is not None:
#                    if q['secure_token'] == flask.request.headers.get('SecureToken'):
#                        print("token secured via header")
#                    elif self.verifyGHSignature(q['secure_token'], flask.request):
#                        print("GitHub Signature verified")
#                    else:
#                        print("Validation Failed!")
#                        flask.abort(403)

                data = flask.request.get_json()
                self.stashAnnouncement([datetime.datetime.now().isoformat(), key, str(data)])
                self.r.publish(key, codecs.encode(pickle.dumps(data, 0), 'base64'))
                return '{}'.format(codecs.encode(pickle.dumps(data, 0), 'base64'))

            else:
                flask.abort(403)

    def addChannel(self, values):
        db_con = sqlite3.connect(self.dbfile)
        db = db_con.cursor()
        output = db.execute("INSERT INTO main.channels (id, key, security, enabled, queryable) VALUES (NULL, ?, ?, ?, ?)", values)
        db_con.commit()
        db_con.close

    def fetchChannels(self):
        db_con = sqlite3.connect(self.dbfile)
        db = db_con.cursor()
        output = db.execute("SELECT * FROM main.channels")
        return (output.fetchall())

    def queryAnnouncement(self, key):
        db_con = sqlite3.connect(self.dbfile)
        db = db_con.cursor()
        output = db.execute("SELECT * FROM main.data WHERE key=:rediskey", {"rediskey": key})
        return(json.dumps(output.fetchall()))

    def stashAnnouncement(self, values):
        db_con = sqlite3.connect(self.dbfile)
        db = db_con.cursor()
        db.execute("INSERT INTO main.data (id, datetime, key, payload) VALUES (NULL, ?, ?, ?)", values)
        db_con.commit()
        db_con.close()

    def verifyGHSignature(self, token, request):
        signature = "sha256="+hmac.new(
            bytes(token , 'utf-8'), 
            msg = request.data, 
            digestmod = hashlib.sha256
            ).hexdigest().lower()
        return hmac.compare_digest(signature, request.headers['X-Hub-Signature-256'])

    def start(self, debugt):
        self.announcer.run(debug=debugt, port=os.environ['VPA_WEBHOST_PORT'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="VoltPop Redis PubSub Target")
    parser.add_argument('--debug', action='store_true', default=False)
    args = parser.parse_args()
    config = yaml.load(open("announcer.yml", "r"), Loader=yaml.SafeLoader)
    a = Announcer()
    a.start(args.debug)
