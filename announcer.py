import argparse
import codecs
import datetime
import flask
import json
import os
import pickle
import redis
import yaml
import sqlite3

class Announcer():
    def __init__(self):
        # create the Flask app
        self.announcer = app = flask.Flask(__name__)
        self.r = redis.StrictRedis(os.environ['VPA_REDIS_HOST'], os.environ['VPA_REDIS_MAP_PORT'], charset="utf8", decode_responses=True)
        self.p = self.r.pubsub()
        self.dbfile = config["dbfile"]
        # Initialize the Announcement Stash
        db_con = sqlite3.connect(self.dbfile)
        db = db_con.cursor()
        db.execute("""CREATE TABLE IF NOT EXISTS main.data (
            datetime TEXT PRIMARY KEY,
            key TEXT NOT NULL,
            payload BLOB NOT NULL);""")

        @app.route('/query/<key>')
        def query_example(key):
            if key in config['query'].keys():
                return '''{}'''.format(queryAnnouncement(key))
            #query = flask.request.args.get('query')

        @app.route('/announce/<key>', methods=['POST'])
        def voltpop_announcement(key):
            if key in config["announce"].keys():
                data = flask.request.get_json()
                self.stashAnnouncement([datetime.datetime.now().isoformat(), key, data])
                self.r.publish('<key>', codecs.encode(pickle.dumps(data, 0), 'base64').decode())
                return '{}'.format(codecs.encode(pickle.dumps(data, 0), 'base64').decode())
            else:
                flask.abort(403)

    def queryAnnouncement(self, key):
        db_con = sqlite3.connect(self.dbfile)

    def stashAnnouncement(self, values):
        db_con = sqlite3.connect(self.dbfile)
        db = db_con.cursor()
        print(str(values))
        db.execute("INSERT INTO main.data VALUES (%s)" %(str(values)))

    def start(self):
        self.announcer.run(debug=True, port=os.environ['VPA_WEBHOST_PORT'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="VoltPop Redis Webserver")
    parser.add_argument('--debug', action='store_true', default=False)
    config = yaml.load(open("announcer.yml", "r"), Loader=yaml.SafeLoader)
    a = Announcer()
    a.start()
