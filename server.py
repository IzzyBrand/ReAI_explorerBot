"""
Should run on Josh's machine.
"""
from flask import Flask
from flask import request
import cPickle as pickle
import sys

from DQN import DQN

app = Flask(__name__)

fpaths = ['camTests/drivingFootage/fblr_240x160_20fps_300s_0.pkl']
model = DQN(fpaths, restore_path="model/tof_model_robot_newreward_2.ckpt",
    save_path="model/tof_model_robot_newreward_3.ckpt")
# model = DQN()
global_step = 0

@app.route('/request_action', methods=['POST'])
def request_action():
    state, reward = pickle.loads(request.data)
    if reward is not None:
        mem = (model.stored_state, model.stored_action, reward, state)
        model.add_memory(mem)
    action = model.get_curr_Q_action(*state)
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
