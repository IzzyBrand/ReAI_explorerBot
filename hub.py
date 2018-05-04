import picamera
import picamera.array
import numpy as np
import cPickle as pickle
import signal
import sys
import time
import hparams as h
from request import request_action
from drive import Driver
from tof_thread import TofWorker

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
    ########################## START SIGNAL HANDLER ##########################
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

    ############################# INIT THE CAMERA #############################
    camera = picamera.PiCamera(framerate=h.FRAMERATE)
    camera.resolution = (h.IMG_HEIGHT, h.IMG_WIDTH)
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

    action = None
    while True:
        start = time.time()
        # send data back to the DQN to get the next action
        action = request_action("http://138.16.161.77:5000", (frame.data, flow.data, worker.tof_array, action))
        if action is not None: driver.move(*action)
        # delay to keep the loop frequency constant
        elapsed = time.time() - start
        delay = 1./h.FREQUENCY - elapsed
        if delay > 1e-4: camera.wait_recording(delay)
        else: print 1./elapsed
