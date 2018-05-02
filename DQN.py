"""
Should run on Josh's machine.
"""
import tensorflow as tf
import hparams as hp

class DQN:
    def __init__(self):
        self.replay_memory = []

        with tf.variable_scope('curr_Q'):
            self.imgC, self.floC, self.senC, self.motC, self.curr_pred = self.build_Q_net(trainable=True)
        with tf.variable_scope('target_Q'):
            self.imgT, self.floT, self.senT, self.motT, self.curr_pred = self.build_Q_net(trainable=False)

        self.assign_op = self.build_assign('curr_Q', 'target_Q')

        self.sess = tf.Session()

    def build_assign(self, copy_from, copy_to):
        from_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES,
                scope=copy_from)
        to_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES,
                scope=copy_to)
        assert len(from_vars) == len(to_vars)
        ops = []
        for i in xrange(len(from_vars)):
            ops.append(tf.assign(to_vars[i], from_vars[i]))
        return tf.group(*ops)

    def build_Q_net(self, trainable=True):
        # TODO: make this have an actually good net architecture
        img_input = tf.placeholder(tf.float32,
                [None, hp.IMG_HEIGHT, hp.IMG_WIDTH, hp.IMG_DEPTH])
        flow_input = tf.placeholder(tf.float32,
                [None, hp.FLOW_HEIGHT, hp.FLOW_WIDTH, hp.FLOW_DEPTH])
        sensor_input = tf.placeholder(tf.float32, [None, hp.SENSOR_DIM])
        motor_input = tf.placeholder(tf.float32, [None, hp.MOTOR_DIM])

        img_feat = tf.layers.conv2d(img_input, 1, 3, trainable=trainable)
        img_feat = tf.layers.flatten(img_feat)
        img_feat = tf.nn.relu(img_feat)
        img_feat = tf.layers.dense(img_feat, 10, trainable=trainable)
        img_feat = tf.nn.relu(img_feat)

        flow_feat = tf.layers.conv2d(flow_input, 1, 3, trainable=trainable)
        flow_feat = tf.layers.flatten(flow_feat)
        flow_feat = tf.nn.relu(flow_feat)
        flow_feat = tf.layers.dense(flow_feat, 10, trainable=trainable)
        flow_feat = tf.nn.relu(flow_feat)

        feat = tf.concat([img_feat, flow_feat,
                sensor_input, motor_input], axis=1)
        feat = tf.layers.dense(feat, hp.ACTION_SPACE_SIZE, trainable=trainable)
        return img_input, flow_input, sensor_input, motor_input, feat








"""
with tf.variable_scope('Q')
with tf.variable_scope('Q_target')

# Create a variable with a random value.
weights = tf.Variable(tf.random_normal([784, 200], stddev=0.35),
                      name="weights")
# Create another variable with the same value as 'weights'.
w2 = tf.Variable(weights.initialized_value(), name="w2")

tf.assign

tf.get_collection

make sure that tf.assign isn't making the target variables trainable
"""

if __name__ == '__main__':
    d = DQN()
