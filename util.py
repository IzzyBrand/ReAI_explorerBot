import numpy as np

import hparams as hp

def get_random_state():
    img = np.random.random((hp.IMG_HEIGHT, hp.IMG_WIDTH, hp.IMG_DEPTH))
    flow = np.random.random((hp.FLOW_HEIGHT, hp.FLOW_WIDTH, hp.FLOW_DEPTH))
    sensor = np.random.random((hp.SENSOR_DIM,))
    motor = np.random.random((hp.MOTOR_DIM,))
    return (img, flow, sensor, motor)

def get_random_mem():
    a = np.random.randint(hp.ACTION_SPACE_SIZE, size=1)
    r = np.random.random((1,))
    return (get_random_state(), a, r, get_random_state())

def get_reward(s_j, a_j, s_jp1):
	return 0
