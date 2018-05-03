from subprocess import Popen, PIPE
import time
import numpy as np
from drive import Driver
import signal
import sys


d = Driver(12,18) # Starts the class for controlling the motors
tof_process = Popen(['./tof_test'], stdout=PIPE, stderr=PIPE) # start the tof sensors 

# kill the tof process when sigint is pressed
def signal_handler(signal, frame):
		d.stop()
		tof_process.terminate()
		print 'tof terminated. Exit.'
		sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

weights = np.array([[ 1.0,  1.5, 1.5, 1.0],
					[-1.5, -0.5, 0.5, 1.5]])

while True:
	try:
		raw_dists = tof_process.stdout.readline().strip()
		dists = np.array([int(i) for i in raw_dists.split('\t')])/255. * 2. - 1.
	except:
		print raw_dists
		continue

	speed, turn = np.matmul(weights, dists)
	if not (dists==1).any():
		print 'Ah'
		turn = turn * 2
	
	print dists
	d.move(speed*50,turn*50)

