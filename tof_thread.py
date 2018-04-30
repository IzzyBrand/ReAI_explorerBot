from threading import Thread
from subprocess import Popen, PIPE
import numpy as np


class TofWorker(Thread):
    def __init__(self, tof_array):
        Thread.__init__(self)
        self.tof_array = tof_array
        self.tof_process = Popen(['./tof_test'], stdout=PIPE, stderr=PIPE) # start the tof sensors

    def run(self):
        while True:
            raw_dists = tof_process.stdout.readline().strip()
    		self.tof_array = np.array([int(i) for i in raw_dists.split('\t')])/255. * 2. - 1.

def main():
    tof_array = np.array([0, 0, 0, 0])
    worker = TofWorker(tof_array)
    worker.daemon = True
    worker.start()
    while True:
        print(tof_array)
    worker.join()

if __name__ == "__main__":
    main()
