"""
Should run on Josh's machine.
"""
from flask import Flask
from flask import request
import cPickle as pickle

app = Flask(__name__)

network = DQN()

@app.route('/action', methods=['POST'])
def action():
    info = pickle.loads(request.data)
    print info
    # Do neural net stuff here
    return pickle.dumps('hello from the server side')
