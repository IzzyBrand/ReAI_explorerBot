from threading import Thread
from subprocess import Popen, PIPE
import numpy as np
import time


class TofWorker(Thread):
    def __init__(self): 
        Thread.__init__(self) 
        self.tof_array = None 
        self.tof_process = Popen(['./tof_test'], stdout=PIPE, stderr=PIPE) # start the tof sensors
        print 'Launched tof_test at PID', self.tof_process.pid

    def run(self):
        while self.tof_process is not None:
            raw_dists = None
            try:
                raw_dists = self.tof_process.stdout.readline().strip()
                self.tof_array = np.array([int(i) for i in raw_dists.split('\t')])/255. * 2. - 1.
            except:
                if raw_dists is not None: print raw_dists

    def close(self):
        self.tof_process.kill()
        self.tof_process = None


def main():
    worker = TofWorker()
    worker.daemon = True
    worker.start()
    for _ in range(100):
        if (worker.tof_array is not None):
            print(worker.tof_array)
        time.sleep(0.1)
    worker.close()
    worker.join()

if __name__ == "__main__":
    main()
