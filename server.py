from flask import Flask
from flask import request
import cPickle as pickle

app = Flask(__name__)

@app.route('/action', methods=['POST'])
def action():
    info = pickle.loads(request.data)
    print info
    # Do neural net stuff here
    return pickle.dumps('hello from the server side')
