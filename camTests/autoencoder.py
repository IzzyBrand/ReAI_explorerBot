import tensorflow as tf
import numpy as np
import pickle
from matplotlib import pyplot as plt
import cv2
import sys

class DataManager():
    def __init__(self, filename=None):
        self.hw = (20,30)
        self.dim = self.hw[0] * self.hw[1]
        if filename is not None:
            self.load(filename)

    def load_from_pkl(self, filename, options = 'rb'):
        self.data = np.zeros([0,self.hw[1], self.hw[0]])
        with open(filename, options) as f:
            while True: 
                try:
                    raw_frame = pickle.load(f, encoding='latin1')/255. * 2 - 1.
                    bw_frame = np.sum(raw_frame,  axis=2)
                    small_frame = np.flipud(cv2.resize(bw_frame, self.hw))
                    self.data = np.append(self.data, np.expand_dims(small_frame,0), axis=0)
                except EOFError:
                    break

        print('Loaded {} items'.format(self.data.shape[0]))
        self.shuffle()

    def load_from_mp4(self, filename):
        self.data = np.zeros([0,self.hw[0], self.hw[1]])
        cap = cv2.VideoCapture(filename)
        # Check if camera opened successfully
        if (cap.isOpened()== False):  print("Error opening video stream or file")
        else: print('Reading from', filename)
        # Read until video is completed
        counter = 0
        while(cap.isOpened()):
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret == True:
                h = frame.shape[0]
                w = int(h * 1.5)
                border = int((frame.shape[1] - w)/2)
                # print w,h,border
                frame = frame[:,border:w+border,:]
                frame = cv2.resize(frame, (30,20))
                bw_frame = np.mean(frame, axis=2)
                self.data = np.append(self.data, np.expand_dims(bw_frame,0), axis=0)
            else: 
                break
        # When everything done, release the video capture object
        cap.release()

        print('Loaded {} items'.format(self.data.shape[0]))
        self.shuffle()

    def load_from_npy(self, filename):
        self.data = np.load(filename)
        print('Loaded {} items'.format(self.data.shape[0]))
        self.shuffle()

    def save_to_npy(self, filename):
        np.save(filename, self.data)

    def shuffle(self):
        self.index = 0
        self.indices = np.arange(self.data.shape[0])
        np.random.shuffle(self.indices)

    def next_batch(self, batch_size):
        if self.index+batch_size < self.data.shape[0]:
            batch = np.take(self.data, self.indices[self.index:self.index+batch_size], axis=0)
            self.index += batch_size
            return batch
        else: 
            print('\nOUT OF DATA AT. RESHUFFLE')
            self.shuffle()
            return self.next_batch(batch_size)


###############################################################################
# NEURAL NET STUFF
###############################################################################

learning_rate = 2e-200
image_size = 600
fc1_size = 200
fc2_size = 64
fc3_size = 200
batch_size = 50

W1 = tf.Variable(tf.random_normal([image_size, fc1_size],stddev=.1))
b1 = tf.Variable(tf.random_normal([fc1_size],stddev=.1))
W2 = tf.Variable(tf.random_normal([fc1_size, fc2_size],stddev=.1))
b2 = tf.Variable(tf.random_normal([fc2_size],stddev=.1))
W3 = tf.Variable(tf.random_normal([fc2_size, fc3_size],stddev=.1))
b3 = tf.Variable(tf.random_normal([fc3_size],stddev=.1))
W4 = tf.Variable(tf.random_normal([fc3_size, image_size],stddev=.1))
b4 = tf.Variable(tf.random_normal([image_size],stddev=.1))

image   = tf.placeholder(tf.float32, [batch_size, image_size])

logits1 = tf.nn.relu(tf.matmul(image, W1) + b1)    # fully connected 1 and ReLu
logits2 = tf.nn.relu(tf.matmul(logits1, W2) + b2)  # fully connected 2 and ReLu
logits3 = tf.nn.relu(tf.matmul(logits2, W3)) + b3  # fully connected 3 and ReLu
reconstruction = tf.matmul(logits3, W4) + b4       # fully connected 4

loss = tf.reduce_mean(tf.pow((reconstruction - image)/image_size, 2))
train = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss)

if __name__ == '__main__':
    print("hi")
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())
    print("setup session")

    losses = []
    d = DataManager()
    d.load_from_pkl('long_frame.pkl')
    # d.load_from_npy('youtubeFootage/car2.npy')
    # d.save_to_npy('youtubeFootage/car2.npy')
    for i in range(10000):
        batch = d.next_batch(batch_size).reshape([batch_size, image_size])
        sess.run(train, feed_dict={image: batch})
        l = sess.run(loss, feed_dict={image: batch})
        print('\rBatch {}\t Loss: {}'.format(i,l))
        losses.append(l)
        # sys.exit()

    print('Final Loss:', losses[-1])

    ############## PLOT LOSS ##############
    plt.plot(losses)
    plt.show()

    ############## VISUALIZE RECONSTRUCTION ##############
    reconstructions = sess.run(reconstruction,feed_dict={image: batch}).reshape([batch_size,20,30])
    plt.imshow(reconstructions[0], cmap='gray')
    plt.show()

    
        




