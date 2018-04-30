from threading import Thread, Lock
from subprocess import Popen, PIPE
import numpy as np


class TofWorker(Thread):
    def __init__(self, tof_array, tof_lock): 
        Thread.__init__(self) 
        self.tof_array = tof_array 
        self.tof_process = Popen(['./tof_test'], stdout=PIPE, stderr=PIPE) # start the tof sensors
        self.tof_lock = tof_lock

    def run(self):
        while True:
            try:
                self.tof_lock.acquire(True)
                raw_dists = self.tof_process.stdout.readline().strip()
                self.tof_array = np.array([int(i) for i in raw_dists.split('\t')])/255. * 2. - 1.
                print >> sys.stderr, self.tof_array
                self.tof_lock.release()
            except:
                print(raw_dists)
                self.tof_lock.release()
            continue

def main():
    tof_array = None
    tof_lock = Lock()
    worker = TofWorker(tof_array, tof_lock)
    worker.daemon = True
    worker.start()
    while True:
        tof_lock.acquire(True)
        if (worker.tof_array is not None):
            print("memes")
            print(worker.tof_array)
        tof_lock.release()
    worker.join()

if __name__ == "__main__":
    main()
