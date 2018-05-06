import numpy as np
import hparams as hp

###############################################################################
# bs data generation
###############################################################################
def get_random_state():
    img = np.random.random((hp.IMG_HEIGHT, hp.IMG_WIDTH, hp.IMG_DEPTH))
    flow = np.random.random((hp.FLOW_HEIGHT, hp.FLOW_WIDTH, hp.FLOW_DEPTH))
    motor = np.random.random((hp.MOTOR_DIM,))
    return (img, flow, motor)

def get_random_mem():
    a = np.random.randint(hp.ACTION_SPACE_SIZE, size=1)
    r = np.random.random((1,))
    return (get_random_state(), a, r, get_random_state())

###############################################################################
#  reward functions
###############################################################################
def motor_reward(motors):
	#motors = (np.array(motors)-1000)/500.
	direction = ((motors > 0).all() * 2) - 1
	return np.abs(np.prod(motors)) * direction

def tof_reward(tof_array):
	return np.min(tof_array) * 2. - 1

def get_reward(s_j, a_j, s_jp1, tof_j, tof_jp1):
	_,_,motors = s_jp1
	alpha = 0.75
	return alpha * tof_reward(tof_jp1) + (1.-alpha) * motor_reward(motors)

###############################################################################
# action/motor conversion
###############################################################################
# generate the arrays for indexing action -> motor output

# gets the motor output for the action
def action_to_motor(action):
	return np.array((m1_deltas[action], m2_deltas[action]))

def motor_to_action(dm1,dm2):
	return np.argmax(np.logical_and((m1_deltas == dm1), (m2_deltas == dm2)))
