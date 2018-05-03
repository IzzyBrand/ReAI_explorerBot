import numpy as np

import hparams as hp

def get_random_state():
    img = np.random.random((hp.IMG_HEIGHT, hp.IMG_WIDTH, hp.IMG_DEPTH))
    flow = np.random.random((hp.FLOW_HEIGHT, hp.FLOW_WIDTH, hp.FLOW_DEPTH))
    sensor = np.random.random((4,))
    motor = np.random.random((2,))
    return (img, flow, sensor, motor)

def get_random_mem():
    a = np.random.randint(hp.ACTION_SPACE_SIZE, size=1)
    r = np.random.random((1,))
    return (get_random_state(), a, r, get_random_state())
