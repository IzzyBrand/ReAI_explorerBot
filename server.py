"""
Should run on Josh's machine.
"""
from flask import Flask
from flask import request
import cPickle as pickle
import sys

from DQN import DQN

app = Flask(__name__)

fpaths = ['good_data/240x160_20fps_60s_0.pkl']
model = DQN(fpaths, restore_path="model/action_model.ckpt")
global_step = 0

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

    global global_step
    model.batch_update(global_step)
    global_step += 1
    # http 204 no content
    print "Done updating"
    return ('', 204)
