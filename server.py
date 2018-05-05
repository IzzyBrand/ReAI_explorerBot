"""
Should run on Josh's machine.
"""
from flask import Flask
from flask import request
import cPickle as pickle
import sys

from DQN import DQN

app = Flask(__name__)

fpaths = ['camTests/drivingFootage/240x180_20fps_60s_0.pkl']
model = DQN(fpaths)

@app.route('/request_action', methods=['POST'])
def request_action():
    state, reward = pickle.loads(request.data)
    action = model.get_curr_Q_action(*state)
    if reward is not None:
        mem = (model.stored_state, model.stored_action, reward, state)
        model.add_memory(mem)
    model.stored_state = state
    model.stored_action = action

    return pickle.dumps(action)

@app.route('/batch_update', methods=['POST'])
def batch_update():
    print "Got request"
    step = int(request.data)
    model.batch_update(step)
    # http 204 no content
    return ('', 204)
