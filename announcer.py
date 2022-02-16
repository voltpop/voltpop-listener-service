import argparse
import codecs
import flask
import json
import os
import pickle
import redis
import yaml

class Announcer():

    def __init__(self):
        # create the Flask app
        self.announcer = app = flask.Flask(__name__)
        self.r = redis.StrictRedis(os.environ['VPA_REDIS_HOST'], os.environ['VPA_REDIS_MAP_PORT'], charset="utf8", decode_responses=True)
        self.p = self.r.pubsub()

        @app.route('/query')
        def query_example():
            query = flask.request.args.get('query')
            return '''{}'''.format(self.p.get_message())

        @app.route('/announce', methods=['POST'])
        def voltpop_announcement():
            data = flask.request.get_json()
            self.r.publish('ansible', codecs.encode(pickle.dumps(data, 0), 'base64').decode())
            return '{}'.format(codecs.encode(pickle.dumps(data, 0), 'base64').decode())

    def start(self):
        self.announcer.run(debug=True, port=os.environ['VPA_WEBHOST_PORT'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="VoltPop Redis Webserver")
    parser.add_argument('--debug', action='store_true', default=False)
    
    a = Announcer()
    a.start()
