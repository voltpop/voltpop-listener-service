import argparse
import codecs
import flask
import json
import os
import pickle
import redis
import yaml

class Announcer():

    def __init__(self, config):
        # create the Flask app
        self.config = config
        self.announcer = app = flask.Flask(__name__)
        self.r = redis.StrictRedis(config['redis_host'], config['redis_port'], charset="utf8", decode_responses=True)
        self.p = self.r.pubsub()

        @app.route('/query')
        def query_example(self):
            query = flask.request.args.get('query')
            return '''{}'''.format(self.p.get_message())

        @app.route('/announce', methods=['POST'])
        def voltpop_announcement(self):
            data = flask.request.get_json()
            self.r.publish('ansible', codecs.encode(pickle.dumps(data, 0), 'base64').decode())
            return '{}'.format(codecs.encode(pickle.dumps(data, 0), 'base64').decode())

    def start(self):
        self.announcer.run(debug=True, port=self.config['webserver_port'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="VoltPop Redis Webserver")
    parser.add_argument('--debug', action='store_true', default=False)
    
    if os.path.isfile('announcer.yml'):
        config = yaml.load(open('announcer.yml', 'r').read(), Loader=yaml.SafeLoader)
    a = Announcer(config)
    a.start()
