"""
Should run on Josh's machine.
"""
from flask import Flask
from flask import request
import cPickle as pickle

from DQN import DQN

app = Flask(__name__)

model = DQN()

@app.route('/request_action', methods=['POST'])
def request_action():
    state = pickle.loads(request.data)
    action = model.get_curr_Q_action(*state)
    # Do neural net stuff here
    return pickle.dumps(action)

@app.route('/add_memory', methods=['POST'])
def add_memory():
    mem = pickle.loads(request.data)
    model.add_memory(mem)
    # http 204 no content
    return ('', 204)

@app.route('/batch_update', methods=['POST'])
def batch_update():
    model.batch_update()
    # http 204 no content
    return ('', 204)
