import flask
import redis
import pickle
import codecs

# create the Flask app
app = flask.Flask(__name__)
r = redis.StrictRedis('127.0.0.1', 6379, charset="utf8", decode_responses=True)
p = r.pubsub()

@app.route('/query')
def query_example():
    query = flask.request.args.get('query')
    return '''{}'''.format(p.get_message())

@app.route('/announce', methods=['POST'])
def voltpop_announcement():
    data = flask.request.get_json()
    r.publish('ansible', codecs.encode(pickle.dumps(data, 0), 'base64').decode())
    return '{}'.format(codecs.encode(pickle.dumps(data, 0), 'base64').decode())

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)
