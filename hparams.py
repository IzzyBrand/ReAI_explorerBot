import numpy as np
########### INPUT PARAMS ###########
FREQUENCY = 2 # loop frequency of the controller
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

MOTOR_VALS = np.array([[ 1.0,  1.0], # F
					   [-0.5, -0.5], # B
					   [ 1.0,  0.0], # L
					   [ 0.0,  1.0]])# R

ACTION_SPACE_SIZE = MOTOR_VALS.shape[0]

DISCOUNT_FACTOR = 0.95
LEARNING_RATE = 1e-7 # TODO: May want to decay by using a tf.Variable
BATCH_SIZE = 100
MEMORY_SIZE = 5000
TARGET_Q_UPDATE_INTERVAL = 50
EPS=0.2

ACTION_TRAIN_LR = 3e-4

