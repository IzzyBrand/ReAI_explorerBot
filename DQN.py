"""
Should run on Josh's machine.
"""
import tensorflow as tf
import hparams as hp
import numpy as np

from collections import deque

import util

class DQN:
    def __init__(self, mem_files = []):
        self.replay_memory = deque(maxlen=hp.MEMORY_SIZE)

        with tf.variable_scope('curr_Q'):
            # Gets input placeholders and net outputs for current Q net
            self.imgC, self.floC, self.motC, self.curr_pred = (
                    self.build_Q_net(trainable=True))
        with tf.variable_scope('target_Q'):
            # Gets input placeholders and net outputs for target Q net
            self.imgT, self.floT, self.motT, self.target_pred = (
                    self.build_Q_net(trainable=False))

        # Action taken at step J
        self.a_j = tf.placeholder(tf.int32, [None])
        # Reward received at step J
        self.r_j = tf.placeholder(tf.float32, [None])

        self.loss = self.build_loss()

        self.train_op = tf.train.GradientDescentOptimizer(
                hp.LEARNING_RATE).minimize(self.loss)

        # Operation used to update the target net to the parameters of the
        # current net.
        self.assign_op = self.build_assign('target_Q', 'curr_Q')

        self.sess = tf.Session()
        self.init_graph()

    def build_loss(self):
        y_j = self.r_j + hp.DISCOUNT_FACTOR * tf.reduce_max(self.target_pred,
                axis=1)
        arange = tf.expand_dims(tf.range(tf.shape(self.a_j)[0]), 1)
        a_j = tf.expand_dims(self.a_j, 1)
        indices = tf.concat([arange, a_j], 1)
        indices = tf.split(indices, 1, axis=0)
        curr_Q_vals = tf.reshape(tf.gather_nd(self.curr_pred, indices), [-1])
        return tf.reduce_mean((y_j - curr_Q_vals) ** 2)

    def build_assign(self, copy_to, copy_from):
        to_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES,
                scope=copy_to)
        from_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES,
                scope=copy_from)
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

        feat = tf.concat([img_feat, flow_feat, motor_input], axis=1)
        feat = tf.layers.dense(feat, hp.ACTION_SPACE_SIZE, trainable=trainable)
        return img_input, flow_input, motor_input, feat

    def init_graph(self):
        self.sess.run(tf.global_variables_initializer())
        self.sess.run(self.assign_op)

    def get_curr_Q_action(self, img, flow, motor):
        fd = {
            self.imgC: np.expand_dims(img, axis=0),
            self.floC: np.expand_dims(flow, axis=0),
            self.motC: np.expand_dims(motor, axis=0)
        }
        Q_vals = self.sess.run(self.curr_pred, feed_dict=fd)
        return np.argmax(Q_vals, axis=1)[0]

    def add_memory(self, mem):
        self.replay_memory.append(mem)

    def load_memory_from_file(self, file):
        with open(sys.argv[1], 'rb') as f:
            counter = 0
            while True:
                try:
                    frame, flow, tof, action = pickle.load(f)
                except:
                    pass

    def batch_update(self):
        idxs = np.random.choice(len(self.replay_memory),
                hp.BATCH_SIZE, replace=False)
        # Get a list of (s_j, a_j, r_j, s_jp1) tuples
        mems = [self.replay_memory[idx] for idx in idxs]
        # Break these into coordinatewise lists, noting that zip is its own inverse!
        # https://stackoverflow.com/questions/19339/transpose-unzip-function-inverse-of-zip
        s_js, a_js, r_js, s_jp1s = zip(*mems)
        # Similarly, break the states into their individual components, and
        # create stacked np arrays for network input.
        img_js, flow_js, motor_js = map(lambda ls:
                np.stack(ls), zip(*s_js))
        img_jp1s, flow_jp1s, motor_jp1s = map(lambda ls:
                np.stack(ls), zip(*s_jp1s))
        a_js = np.concatenate(a_js)
        r_js = np.concatenate(r_js)

        fd = {
            self.imgC: img_js,
            self.floC: flow_js,
            self.motC: motor_js,
            self.imgT: img_jp1s,
            self.floT: flow_jp1s,
            self.motT: motor_jp1s,
            self.a_j: a_js,
            self.r_j: r_js,
        }

        curr_loss, _ = self.sess.run([self.loss, self.train_op], feed_dict=fd)
        print 'Current loss: ' + str(curr_loss)





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
    for i in xrange(1050):
        d.add_memory(util.get_random_mem())
    d.batch_update()
