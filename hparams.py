########### INPUT PARAMS ###########
IMG_HEIGHT = 108
IMG_WIDTH = 192
IMG_DEPTH = 3 * 4 # 3 color channels, 4 frame history

FLOW_HEIGHT = 25
FLOW_WIDTH = 25
FLOW_DEPTH = 4 # 1 color channel, 4 frame history

MOTOR_DIM = 2

SENSOR_DIM = 4

########### OTHER STUFF ###########
ACTION_SPACE_SIZE = 3 * 3 # forward, nothing, backward for each motor

DISCOUNT_FACTOR = 0.9

# TODO: May want to decay by using a tf.Variable
LEARNING_RATE = 3e-4
