import pickle
import numpy as np
from matplotlib import pyplot as plt

frame = None

with open('long_frame.pkl', 'rb') as f:
    while True: 
        try:
            frame = pickle.load(f, encoding='latin1')
            plt.imshow(frame)
            plt.show()
        except EOFError:
            break