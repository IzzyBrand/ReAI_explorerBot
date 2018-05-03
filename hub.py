import picamera
import picamera.array
import numpy as np
import cPickle as pickle
import signal
import sys
import time
from request import request_action
from drive import Driver

# TOF Sensor Stuff
class TofWorker(Thread):
    def __init__(self, tof_array, tof_lock):
        Thread.__init__(self)
        self.tof_array = tof_array
        self.tof_process = Popen(['./tof_test'], stdout=PIPE, stderr=PIPE) # start the tof sensors
        self.tof_lock = tof_lock

    def run(self):
        while True:
            try:
                self.tof_lock.acquire(True) # We may not need to lock
                raw_dists = self.tof_process.stdout.readline().strip()
                self.tof_array = np.array([int(i) for i in raw_dists.split('\t')])/255. * 2. - 1.
                print >> sys.stderr, self.tof_array
                self.tof_lock.release() # We may not need to lock
            except:
                print(raw_dists)
                self.tof_lock.release() # We may not need to lock
            continue

    def get_tof_data():
        tof_lock.acquire(True) # We may not need to lock
        if (worker.tof_array is not None):
            print("memes")
            print(worker.tof_array)
            ret = np.copy(worker.tof_array)
        tof_lock.release() # We may not need to lock
        return ret

class FrameAnalyzer(picamera.array.PiRGBAnalysis):
    def setup(self, filename=None):
        self.data = None
        if filename is not None: self.file = open(filename, 'ab')
        else: self.file = None

    def analyse(self, array):
        self.data = array
        if self.file is not None: pickle.dump(array, self.file)

    def close(self):
        if self.file is not None: self.file.close()


class FlowAnalyzer(picamera.array.PiMotionAnalysis):
    def setup(self, filename=None):
        self.data = None
        if filename is not None: self.file = open(filename, 'ab')
        else: self.file = None

    def analyse(self, array):
        self.data = array
        if self.file is not None: pickle.dump(array, self.file)

    def close(self):
        if self.file is not None: self.file.close()

functions_to_call_on_exit = []

# kill a bunch of things on exit
def signal_handler(signal, frame):
        for f in functions_to_call_on_exit:
            print f
            f()
        sys.exit(0)


framerate = 15
width, height = 160, 120

if __name__ == '__main__':
    ########################### INIT THE TOF SENSOR ###########################
    # TODO: Initialize threading module to read from the TOF sensor

    tof_array = None
    tof_lock = Lock()
    worker = TofWorker(tof_array, tof_lock)
    worker.daemon = True
    worker.start()

    ############################# INIT THE DRIVER #############################
    driver = Driver(12,18)
    functions_to_call_on_exit.append(driver.stop)

    ############################# INIT THE CAMERA #############################
    signal.signal(signal.SIGINT, signal_handler)
    camera = picamera.PiCamera(framerate=90)
    camera.resolution = (width, height)
    frame = FrameAnalyzer(camera)
    flow = FlowAnalyzer(camera)
    frame.setup()
    flow.setup()
    camera.start_recording("/dev/null", format='h264',
        splitter_port=1, motion_output=flow)
    camera.start_recording(frame, format='rgb',
        splitter_port=2)

    functions_to_call_on_exit.append(frame.close)
    functions_to_call_on_exit.append(flow.close)
    functions_to_call_on_exit.append(lambda:
        camera.stop_recording(splitter_port=1))
    functions_to_call_on_exit.append(lambda:
        camera.stop_recording(splitter_port=2))

    ############################ INIT THE THE NET ############################
    # TODO: Something with tensorflow

    ############################## RUN THE TRAP ##############################
    print('Giving all the things a moment to boot up')
    time.sleep(5)
    print('HERE WE GO')
    while True:
        print request_action("http://138.16.161.77:5000", (frame.data, flow.data, np.zeros(4), np.zeros(2)))
        driver.stop()
        worker.join()
