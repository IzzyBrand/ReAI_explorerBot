import numpy as np
import hparams as hp

def get_random_state():
    img = np.random.random((hp.IMG_HEIGHT, hp.IMG_WIDTH, hp.IMG_DEPTH))
    flow = np.random.random((hp.FLOW_HEIGHT, hp.FLOW_WIDTH, hp.FLOW_DEPTH))
    motor = np.random.random((hp.MOTOR_DIM,))
    return (img, flow, motor)

def get_random_mem():
    a = np.random.randint(hp.ACTION_SPACE_SIZE, size=1)
    r = np.random.random((1,))
    return (get_random_state(), a, r, get_random_state())

def get_reward(s_j, a_j, s_jp1, tof_j, tof_jp1):
	return 0

# generate the arrays for indexing action -> motor output
m1, m2 = np.meshgrid(hp.MOTOR_VALS, hp.MOTOR_VALS)
m1 = np.ravel(m1) 
m2 = np.ravel(m2)

# gets the motor output for the action
def action_to_motor(action):
	return m1[action], m2[action]

def motor_to_action(dm1,dm2):
	return np.argmax(np.logical_and((m1 == dm1), (m2 == dm2)))
