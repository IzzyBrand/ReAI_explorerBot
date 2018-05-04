########### INPUT PARAMS ###########
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
ACTION_SPACE_SIZE = 3 * 3 # forward, nothing, backward for each motor

DISCOUNT_FACTOR = 0.9

# TODO: May want to decay by using a tf.Variable
LEARNING_RATE = 3e-4

MEMORY_SIZE = 1000

BATCH_SIZE = 100

########### NET PARAMS ###########
IMG_CONV_LAYERS = 5
FLOW_CONV_LAYERS = 4
MOTOR_FC_LAYERS = 3
