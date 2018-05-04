import picamera
import picamera.array
import numpy as np
import cPickle as pickle
import signal
import sys
import time
from request import request_action
from drive import Driver
from tof_thread import TofWorker

speed = 0
turn = 0

class FrameAnalyzer(picamera.array.PiRGBAnalysis):
    def setup(self, filename=None):
        self.data = None
        if filename is not None: self.file = open(filename + "_frame.pkl", 'ab')
        else: self.file = None

    def analyse(self, array):
        self.data = array
        if self.file is not None: pickle.dump(array, self.file)

    def close(self):
        if self.file is not None: self.file.close()


class FlowAnalyzer(picamera.array.PiMotionAnalysis):
    def setup(self, filename=None):
        self.data = None
        if filename is not None: self.file = open(filename + "_flow.pkl", 'ab')
        else: self.file = None

    def analyse(self, array):
        self.data = array
        if self.file is not None: pickle.dump((array,speed,turn), self.file)

    def close(self):
        if self.file is not None: self.file.close()

functions_to_call_on_exit = []

# kill a bunch of things on exit
def signal_handler(signal, frame):
    for f in functions_to_call_on_exit:
        print f[0]
        f[1]()
    print 'EXITING'
    sys.exit(0)


framerate = 15
width, height = 160, 120

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    ########################### INIT THE TOF SENSOR ###########################
    # TODO: Initialize threading module to read from the TOF sensor
    worker = TofWorker()
    worker.daemon = True
    worker.start()
    functions_to_call_on_exit.append(("Closing TOF subrocess", worker.close))
    functions_to_call_on_exit.append(("Joining TOF thread", worker.join))

    ############################# INIT THE DRIVER #############################
    driver = Driver(12,18)
    functions_to_call_on_exit.append(("Closing servod process", driver.close))
    tof_drive_weights = np.array([[ 1.0,  1.5, 1.5, 1.0],
                                  [-1.5, -0.5, 0.5, 1.5]])

    ############################# INIT THE CAMERA #############################
    camera = picamera.PiCamera(framerate=30)
    camera.resolution = (width, height)
    frame = FrameAnalyzer(camera)
    flow = FlowAnalyzer(camera)
    if len(sys.argv) > 1:
        print "Saving camera data to", sys.argv[1]
        frame.setup(sys.argv[1])
        flow.setup(sys.argv[1])
    else:
        frame.setup()
        flow.setup()
    camera.start_recording("/dev/null", format='h264',
        splitter_port=1, motion_output=flow)
    camera.start_recording(frame, format='rgb',
        splitter_port=2)

    functions_to_call_on_exit.append(("Closing frame writer", frame.close))
    functions_to_call_on_exit.append(("Closing flow writer", flow.close))
    functions_to_call_on_exit.append(("Closing splitter 1", lambda:
        camera.stop_recording(splitter_port=1)))
    functions_to_call_on_exit.append(("Closing splitter 2", lambda:
        camera.stop_recording(splitter_port=2)))

    ############################## RUN THE TRAP ##############################
    print('Giving all the things a moment to boot up')
    time.sleep(5)
    print('HERE WE GO')
    start = time.time()
    while time.time() - start < 30:
        dists = worker.tof_array
        if dists is not None:
            speed, turn = np.matmul(tof_drive_weights, dists)
            if not (dists==1).any():
                print 'Ah'
                turn = turn * 2
            
            print dists
            driver.move(speed*50,turn*50)
        else: 
            print "dists is None"
            time.sleep(0.2)
            
    signal_handler(0, 0)