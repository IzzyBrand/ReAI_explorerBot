import cPickle as pickle
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
import sys

matplotlib.use('GTK')

frame = None
if len(sys.argv) < 2:
    print 'Specify a filename to read from'
    sys.exit(1)
print 'Reading from', sys.argv[1]

with open(sys.argv[1], 'rb') as f:
    counter = 0
    while True:
        try:
            frame = pickle.load(f)
            counter += 1
        except EOFError:
            break

    print 'Loaded {} frames'.format(counter)
    print(frame)
    plt.imshow(frame)
    plt.show()
