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
import util

class FrameAnalyzer(picamera.array.PiRGBAnalysis):
    def setup(self):
        self.data = None

    def analyse(self, array):
        self.data = array


class FlowAnalyzer(picamera.array.PiMotionAnalysis):
    def setup(self):
        self.data = None
    def analyse(self, array):
        self.data = array

functions_to_call_on_exit = []

# kill a bunch of things on exit
def signal_handler(signal, frame):
    for f in functions_to_call_on_exit:
        print f[0]
        f[1]()
    print 'EXITING'
    sys.exit(0)

if __name__ == '__main__':
    ########################### OPEN FIL AND SIGNAL ###########################
    if len(sys.argv) < 2: 
        print 'Please specify a filename'
        sys.exit(1)

    print 'Recording to', sys.argv[1]
    f = open(sys.argv[1], 'ab')
    functions_to_call_on_exit.append(("Closing " + sys.argv[1], f.close))

    signal.signal(signal.SIGINT, signal_handler)

    ########################### INIT THE TOF SENSOR ###########################
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
    camera = picamera.PiCamera(framerate=h.FRAMERATE)
    camera.resolution = (h.IMG_WIDTH, h.IMG_HEIGHT)
    frame = FrameAnalyzer(camera)
    flow = FlowAnalyzer(camera)

    frame.setup()
    flow.setup()
    camera.start_recording("/dev/null", format='h264',
        splitter_port=1, motion_output=flow)
    camera.start_recording(frame, format='rgb',
        splitter_port=2)

    functions_to_call_on_exit.append(("Closing splitter 1", lambda:
        camera.stop_recording(splitter_port=1)))
    functions_to_call_on_exit.append(("Closing splitter 2", lambda:
        camera.stop_recording(splitter_port=2)))

    ############################## RUN THE TRAP ##############################
    print('Giving all the things a moment to boot up')
    time.sleep(5)
    print('HERE WE GO')

    frequency = 20.
    duration = 300
    timer_start = time.time()
    while time.time() - timer_start < duration:
        start = time.time()
        dists = worker.tof_array
        if dists is not None:
            action = 4 # TODO, generate the action from the dists
            m1, m2 = util.action_to_motor(action)
            driver.dmotor(m1, m2)
            # each x_j should be a tuple of (frame, flow, motor, action, tof)
            x_j = (frame.data, flow.data, (driver.m1, driver.m2), action, dists)
            pickle.dump(x_j, f)

        else: print "dists is None"

        elapsed = time.time() - start
        delay = 1./h.FREQUENCY - elapsed
        if delay > 1e-4: camera.wait_recording(delay)
        else: print 1./elapsed

    signal_handler(0, 0) # exit
