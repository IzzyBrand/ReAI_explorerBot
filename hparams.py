import numpy as np
########### INPUT PARAMS ###########
FREQUENCY = 10 # loop frequency of the controller
FRAMERATE = 20 # framerate of the camera

HISTORY_LEN = 1
IMG_HEIGHT = 160
IMG_WIDTH = 240
IMG_DEPTH = 3 * HISTORY_LEN # 3 color channels, 4 frame history

FLOW_HEIGHT = 10
FLOW_WIDTH = 16
FLOW_DEPTH = 3 * HISTORY_LEN # 1 color channel, 4 frame history

MOTOR_DIM = 2 * HISTORY_LEN
SENSOR_DIM = 4 * HISTORY_LEN

########### OTHER STUFF ###########
DQN_URL = "http://agni:5000"

MOTOR_VALS = np.array([-0.1,0,0.1]) # forward, nothing, backward for each motor
ACTION_SPACE_SIZE = MOTOR_VALS.shape[0]**2

DISCOUNT_FACTOR = 0.9
LEARNING_RATE = 3e-7 # TODO: May want to decay by using a tf.Variable
BATCH_SIZE = 10
MEMORY_SIZE = 1000

EPS = 0.1
TARGET_Q_UPDATE_INTERVAL = 200

########### NET PARAMS ###########
IMG_CONV_LAYERS = 4
FLOW_CONV_LAYERS = 4
MOTOR_FC_LAYERS = 3
