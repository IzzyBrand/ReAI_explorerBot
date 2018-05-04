import numpy as np
########### INPUT PARAMS ###########
FREQUENCY = 10 # loop frequency of the controller
FRAMERATE = 20 # framerate of the controller

HISTORY_LEN = 4
IMG_HEIGHT = 112
IMG_WIDTH = 192
IMG_DEPTH = 3 * HISTORY_LEN # 3 color channels, 4 frame history

FLOW_HEIGHT = 25
FLOW_WIDTH = 25
FLOW_DEPTH = 3 * HISTORY_LEN # 1 color channel, 4 frame history

MOTOR_DIM = 2 * HISTORY_LEN

SENSOR_DIM = 4 * HISTORY_LEN

########### OTHER STUFF ###########
MOTOR_VALS = np.array([-10,0,10]) # forward, nothing, backward for each motor
ACTION_SPACE_SIZE = MOTOR_VALS.shape[0]**2

DISCOUNT_FACTOR = 0.9

# TODO: May want to decay by using a tf.Variable
LEARNING_RATE = 3e-4

MEMORY_SIZE = 1000

BATCH_SIZE = 100

########### NET PARAMS ###########
IMG_CONV_LAYERS = 5
FLOW_CONV_LAYERS = 4
MOTOR_FC_LAYERS = 3
