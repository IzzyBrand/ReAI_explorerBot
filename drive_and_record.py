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
import hparams as h
from copy import deepcopy

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
    f = open(sys.argv[1], 'wb')
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
    # array of weights to generate desired speed and turn from tof_array
    # tof_drive_weights = np.array([[ 1.0,  1.5, 1.5, 1.0],
    #                               [-1.5, -0.5, 0.5, 1.5]])
    # array of weight to generate desired motor1 and motor2 speeds
    w = np.array([1,  .65, .45, -.4])
    direct_drive_weights = np.vstack([w, np.flip(w, axis=0)])
    
    #direct_drive_weights = np.array([[ 2.,  1.5,  1.,  -1.],
    #                                 [-1.,  1.,  1.5,  2.]])

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

    duration = 300
    max_motor_delta = h.MOTOR_VALS[-1]
    timer_start = time.time()
    a_j   = None
    a_jp1 = None
    s_j   = None
    tof_j = None
    while time.time() - timer_start < duration:
        start = time.time()
        # we're now in state j+1, called s_jp1
        motors = deepcopy(driver.m)
        s_jp1 = (frame.data, flow.data, motors)
        tof_jp1 = deepcopy(worker.tof_array)
        # so we can calculate the reward, (s_j, a_j, s_jp1) -> r_j
        #r_j = None if tof_j is None else \
        #     util.get_reward(s_j, a_j, s_jp1, tof_j, tof_jp1)
        # and request an action for s_jp1 -> a_jp1
        if tof_jp1 is not None:
            
            if (tof_jp1 == 1).all(): a_jp1 = 0
            elif (tof_jp1[1:3] < 1).all(): a_jp1 = 1
            elif (tof_jp1[3] < 1): a_jp1 = 2
            else: a_jp1 = 3

            # each x_j should be a tuple of (frame, flow, motor, action, tof)
            x_jp1 = s_jp1 + (a_jp1, tof_jp1)
         
            # print "Reward j: {}\t Action j+1: {}".format(r_j, a_jp1)
            driver.act(a_jp1)
            pickle.dump(x_jp1, f)

        else: print "dists is None"

        # once we've taken that action, move ahead a timestep
        s_j = s_jp1
        a_j = a_jp1
        tof_j = tof_jp1

        # delay to keep the loop frequency constant
        elapsed = time.time() - start
        delay = 1./h.FREQUENCY - elapsed
        if delay > 1e-4: camera.wait_recording(delay)
        else: print 1./elapsed
    signal_handler(0, 0) # exit
