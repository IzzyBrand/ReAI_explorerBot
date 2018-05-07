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
import time

class DQN:
    def __init__(self, mem_files = [], restore_path = None, save_path = "irl/model.ckpt"):
        self.replay_memory = deque(maxlen=hp.MEMORY_SIZE)
        for f in mem_files: self.add_file_to_memory(f)
        with tf.variable_scope('curr_Q'):
            # Gets input placeholders and net outputs for current Q net
            self.motC, self.tofC, self.curr_pred = \
                    self.build_Q_net(trainable=True)
        with tf.variable_scope('target_Q'):
            # Gets input placeholders and net outputs for target Q net
            self.motT, self.tofT, self.target_pred = \
                    self.build_Q_net(trainable=False)

        # Action taken at step J
        self.a_j = tf.placeholder(tf.int32, [None])
        # Reward received at step J
        self.r_j = tf.placeholder(tf.float32, [None])

        # stores the previous state and action so they can be added to the
        # memory once we have received the reward (in the flask app)
        self.stored_state = None
        self.stored_action = None

        self.loss = self.build_loss()
        self.action_ph, self.action_loss = self.build_action_loss()

        # Note: changing this to AdamOptimizer breaks the assertion in
        # build assign because the optimizer stores a lot of global
        # variables to handle momentum
        self.train_op = tf.train.GradientDescentOptimizer(
                hp.LEARNING_RATE).minimize(self.loss)

        self.train_action_op = tf.train.GradientDescentOptimizer(
                hp.ACTION_TRAIN_LR).minimize(self.action_loss)

        # Operation used to update the target net to the parameters of the
        # current net.
        self.assign_op = self.build_assign('target_Q', 'curr_Q')

        self.sess = tf.Session()
        self.init_graph()

        self.merged = tf.summary.merge_all()

        logdirstring = "logs/log" + str(int(time.time()))
        for x in dir(hp):
            if x.isupper():
                logdirstring += "_"
                logdirstring += str(getattr(hp, x))
        logdirstring += "/"
        self.writer = tf.summary.FileWriter(logdirstring, self.sess.graph)

        self.save_path = save_path

        self.saver = tf.train.Saver()

        if (restore_path is not None):
            self.saver.restore(self.sess, restore_path)
            print("Restored model from " + str(restore_path))

    def build_loss(self):
        y_j         = self.r_j + hp.DISCOUNT_FACTOR \
                    * tf.reduce_max(self.target_pred, axis=1)
        arange      = tf.expand_dims(tf.range(tf.shape(self.a_j)[0]), 1)
        a_j         = tf.expand_dims(self.a_j, 1)
        indices     = tf.concat([arange, a_j], 1)
        indices     = tf.split(indices, 1, axis=0)
        curr_Q_vals = tf.reshape(tf.gather_nd(self.curr_pred, indices), [-1])
        loss        = tf.reduce_mean((y_j - curr_Q_vals) ** 2)
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

    def build_action_loss(self):
        action = tf.placeholder(tf.int32, [None, hp.ACTION_SPACE_SIZE])
        x_ent = tf.nn.softmax_cross_entropy_with_logits(logits=self.curr_pred, labels=action)
        return action, tf.reduce_mean(x_ent)

    def build_Q_net(self, trainable=True):
        motor_input = tf.placeholder(tf.float32, [None, hp.MOTOR_DIM])
        tof_input = tf.placeholder(tf.float32, [None, hp.SENSOR_DIM])

        motor_feat = motor_input
        tof_feat = tof_input
        feat = tf.concat([tof_feat, motor_input], axis=1)
        feat = tf.layers.dense(feat, 20, trainable=trainable)
        feat = tf.nn.relu(feat)
        feat = tf.layers.dense(feat, 6, trainable=trainable)
        feat = tf.nn.relu(feat)
        feat = tf.layers.dense(feat, hp.ACTION_SPACE_SIZE, trainable=trainable)
        
        return motor_input, tof_input, feat

    def init_graph(self):
        self.sess.run(tf.global_variables_initializer())
        self.sess.run(self.assign_op)

    def get_curr_Q_action(self, motor, tof):
        if np.random.random() < hp.EPS:
            return np.random.randint(hp.ACTION_SPACE_SIZE)

        fd = {
            self.motC: np.expand_dims(motor, axis=0),
            self.tofC: np.expand_dims(tof, axis=0)
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
                        m_j     = x_j[2]
                        a_j     = x_j[3]
                        tof_j   = x_j[4]
                        m_jp1   = x_jp1[2]
                        tof_jp1 = x_jp1[4]
                        s_j = (m_j, tof_j)
                        s_jp1 = (m_jp1, tof_jp1)
                        r_j = util.get_reward(s_j, a_j, s_jp1, tof_j, tof_jp1)
                        self.add_memory((s_j, a_j, r_j, s_jp1))
                except EOFError:
                    break
            print 'Added {} memories to memory.'.format(count)

    def batch_update(self, global_step):
        idxs = np.random.choice(len(self.replay_memory),
                hp.BATCH_SIZE, replace=False)
        # Get a list of (s_j, a_j, r_j, s_jp1) tuples
        mems = [self.replay_memory[idx] for idx in idxs]
        # Break these into coordinatewise lists, noting that zip is its own inverse!
        # https://stackoverflow.com/questions/19339/transpose-unzip-function-inverse-of-zip
        s_js, a_js, r_js, s_jp1s = zip(*mems)
        # Similarly, break the states into their individual components, and
        # create stacked np arrays for network input.
        motor_js, tof_js = map(lambda ls:
                np.stack(ls), zip(*s_js))
        motor_jp1s, tof_jp1s = map(lambda ls:
                np.stack(ls), zip(*s_jp1s))

        fd = {
            self.motC: motor_js,
            self.tofC: tof_js,
            self.motT: motor_jp1s,
            self.tofT: tof_jp1s,
            self.a_j:  np.array(a_js),
            self.r_j:  np.array(r_js)
        }

        summary, curr_loss, _ = self.sess.run([self.merged, self.loss, self.train_op], feed_dict=fd)

        self.writer.add_summary(summary, global_step)

        if global_step % hp.TARGET_Q_UPDATE_INTERVAL == 0:
            self.update_target_Q()
        if global_step % 50 == 0:
            print "SAVING YO"
            self.saver.save(self.sess, self.save_path)
        return curr_loss

    def update_target_Q(self):
        self.sess.run(self.assign_op)

    def train_action(self, batch):
        _, _, motor_js,  a_js, tof_js = zip(*batch)

        fd = {
            self.motC: np.stack(motor_js),
            self.tofC: np.stack(tof_js),
            self.action_ph:  np.eye(hp.ACTION_SPACE_SIZE)[np.array(a_js)]
        }

        curr_loss, _ = self.sess.run([self.action_loss, self.train_action_op], feed_dict=fd)
        return curr_loss



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
    #d = DQN(sys.argv[1:], save_path="model/action_model.ckpt")
    d = DQN(sys.argv[1:], save_path="model/tof_model.ckpt")
    print("Started a DQN")
    for i in xrange(10001):
        print d.batch_update(i)
        if i%100 ==0: d.saver.save(d.sess, d.save_path)
    sys.exit(0)
    d.sess.run(d.assign_op)
    batch = []
    counter = 0
    step = 0
    for loop_num in range(100):
        for filename in sys.argv[1:]:
            with open(filename, 'rb') as f:
                while True:
                    try:
                        batch.append(pickle.load(f))
                        counter += 1
                    except:
                        break
                    if counter == hp.BATCH_SIZE:
                        print step, d.train_action(batch)
                        batch = []
                        counter = 0
                        step += 1
        d.sess.run(d.assign_op)
        print 'SAVING', filename
        d.saver.save(d.sess, d.save_path)
