"""
Should run on Josh's machine.
"""
import tensorflow as tf
import hparams as hp
import numpy as np
import sys
import cPickle as pickle

from collections import deque

import util

class DQN:
    def __init__(self, mem_files = []):
        self.replay_memory = deque(maxlen=hp.MEMORY_SIZE)
        for f in mem_files: self.add_file_to_memory(f)
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

        self.stored_state = None
        self.stored_action = None

        self.loss = self.build_loss()

        self.train_op = tf.train.GradientDescentOptimizer(
                hp.LEARNING_RATE).minimize(self.loss)

        # Operation used to update the target net to the parameters of the
        # current net.
        self.assign_op = self.build_assign('target_Q', 'curr_Q')

        self.sess = tf.Session()
        self.init_graph()

        self.merged = tf.summary.merge_all()

        logdirstring = "logs/log"
        for x in dir(hp):
            if x.isupper():
                logdirstring += "_"
                # logdirstring += str(x)
                # logdirstring += "-"
                logdirstring += str(getattr(hp, x))
        logdirstring += "/"
        self.writer = tf.summary.FileWriter(logdirstring, self.sess.graph)

    def build_loss(self):
        y_j = self.r_j + hp.DISCOUNT_FACTOR * tf.reduce_max(self.target_pred,
                axis=1)
        arange = tf.expand_dims(tf.range(tf.shape(self.a_j)[0]), 1)
        a_j = tf.expand_dims(self.a_j, 1)
        indices = tf.concat([arange, a_j], 1)
        indices = tf.split(indices, 1, axis=0)
        curr_Q_vals = tf.reshape(tf.gather_nd(self.curr_pred, indices), [-1])
        loss = tf.reduce_mean((y_j - curr_Q_vals) ** 2)
        tf.summary.scalar('loss', loss)
        return loss

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

    def apply_convolution(self, input, output_depth, filter_size, trainable=None):
        input = tf.layers.conv2d(input, output_depth, filter_size,
                trainable=trainable)
        input = tf.layers.batch_normalization(input, trainable=trainable)
        input = tf.nn.relu(input)
        return input

    def build_Q_net(self, trainable=True):
        img_input = tf.placeholder(tf.float32,
                [None, hp.IMG_HEIGHT, hp.IMG_WIDTH, hp.IMG_DEPTH])
        flow_input = tf.placeholder(tf.float32,
                [None, hp.FLOW_HEIGHT, hp.FLOW_WIDTH, hp.FLOW_DEPTH])
        motor_input = tf.placeholder(tf.float32, [None, hp.MOTOR_DIM])

        img_feat = img_input
        for _ in xrange(hp.IMG_CONV_LAYERS):
            img_feat = self.apply_convolution(img_feat, 3, 3, trainable=trainable)
        img_feat = tf.layers.flatten(img_feat)
        img_feat = tf.layers.dense(img_feat, 10, trainable=trainable)
        img_feat = tf.nn.relu(img_feat)

        flow_feat = flow_input
        for _ in xrange(hp.FLOW_CONV_LAYERS):
            flow_feat = self.apply_convolution(flow_feat, 3, 3, trainable=trainable)
        flow_feat = tf.layers.flatten(flow_feat)
        flow_feat = tf.layers.dense(flow_feat, 10, trainable=trainable)
        flow_feat = tf.nn.relu(flow_feat)

        motor_feat = motor_input
        for _ in xrange(hp.MOTOR_FC_LAYERS):
            motor_feat = tf.layers.dense(motor_feat, 10, trainable=trainable)
            motor_feat = tf.nn.relu(motor_feat)

        feat = tf.concat([img_feat, flow_feat, motor_input], axis=1)
        feat = tf.layers.dense(feat, 30, trainable=trainable)
        feat = tf.nn.relu(feat)
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

    def add_file_to_memory(self, filename):
        with open(filename, 'rb') as f:
            count = 0
            x_j = None
            x_jp1 = None
            # each x_j should be a tuple of (frame, flow, motor, action, tof)
            while True:
                try:
                    x_j = x_jp1
                    x_jp1 = pickle.load(f)
                    if x_jp1 is not None and x_j is not None:
                        count += 1
                        s_j     = x_j[:3]
                        a_j     = x_j[3]
                        tof_j   = x_j[4]
                        s_jp1   = x_jp1[:3]
                        tof_jp1 = x_jp1[4]
                        r_j = util.get_reward(s_j, a_j, s_jp1, tof_j, tof_jp1)
                        self.add_memory((s_j, a_j, r_j, s_jp1))
                except EOFError:
                    break
            print 'Added {} memories to memory.'.format(count)

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

        #a_js = np.concatenate(a_js)
        #r_js = np.concatenate(r_js)

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

        summary, curr_loss, _ = self.sess.run([self.merged, self.loss, self.train_op], feed_dict=fd)
        print 'Current loss: ' + str(curr_loss)

        self.writer.add_summary(summary, global_step)


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
    d = DQN(sys.argv[1:])
    # for i in xrange(1050):
    #     d.add_memory(util.get_random_mem())
    for i in xrange(20):
        d.batch_update(i)
