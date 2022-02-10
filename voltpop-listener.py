import flask
from pubsub import pub

def ansible_update(data=None):
    print(data)

pub.subscribe(ansible_update, "ansible")

# create the Flask app
app = flask.Flask(__name__)

@app.route('/query')
def query_example():
    query = flask.request.args.get('query')
    return '''<h1>The query value is: {}</h1>'''.format(query)

@app.route('/announce', methods=['POST'])
def voltpop_announcement():
    r = flask.request.get_json()
    pub.sendMessage("ansible", data=r)
    return '{}'.format(r)

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)
