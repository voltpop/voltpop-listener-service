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
        self.announcer = app = flask.Flask(__name__)
        
        # PubSub configuration
        self.r = redis.StrictRedis(os.environ['VPA_REDIS_HOST'], os.environ['VPA_REDIS_MAP_PORT'], charset="utf8", decode_responses=True, socket_keepalive=True, socket_timeout=300)
        self.p = self.r.pubsub()
        self.dbfile = config["dbfile"]

        # Initialize the Announcement Stash
        db_con = sqlite3.connect(self.dbfile)
        db = db_con.cursor()

        db.execute("""CREATE TABLE IF NOT EXISTS main.data (
            id INTEGER PRIMARY KEY,
            datetime TEXT NOT NULL,
            key TEXT NOT NULL,
            payload BLOB NOT NULL);""")
        db_con.commit()
        db_con.close()

        @app.route('/query/<key>', methods=["GET"])
        def query_example(key):
            if key in config['announcer'].keys() and config['announcer'][key]["queryable"]:
                return '''{}'''.format(self.queryAnnouncement(key))
            #query = flask.request.args.get('query')

        @app.route('/announce/<key>', methods=['POST'])
        def voltpop_announcement(key):
            if key in config["announcer"].keys():
                q = config['announcer'][key]

                # Security!!!
                if q['security'] and q['secure_token'] is not None:
                    if q['secure_token'] == flask.request.headers.get('SecureToken'):
                        print("token secured via header")
                    elif self.verifyGHSignature(q['secure_token'], flask.request):
                        print("GitHub Signature verified")
                    else:
                        print("Validation Failed!")
                        flask.abort(403)

                data = flask.request.get_json()
                self.stashAnnouncement([datetime.datetime.now().isoformat(), key, str(data)])
                self.r.publish(key, codecs.encode(pickle.dumps(data, 0), 'base64'))
                return '{}'.format(codecs.encode(pickle.dumps(data, 0), 'base64'))

            else:
                flask.abort(403)

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
