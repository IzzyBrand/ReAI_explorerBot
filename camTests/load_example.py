import pickle
import numpy as np
from matplotlib import pyplot as plt

frame = None

with open('flow.pkl', 'rb') as f:
    while True: 
        try:
            frame = pickle.load(f)
        except EOFError:
            break

plt.imshow(frame)
plt.show()