import picamera
import picamera.array
import numpy as np
import cPickle as pickle
import signal
import sys
import time
import hparams as h
from request import request_action, batch_update
from drive import Driver
from tof_thread import TofWorker
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
    step_count = 0
    a_j = None
    s_j = None
    tof_j = None
    while True:
        start = time.time()
        # we're now in state j+1, called s_jp1
        motors = deepcopy(driver.m)
        s_jp1 = (frame.data, flow.data, motors)
        tof_jp1 = deepcopy(worker.tof_array)
        # so we can calculate the reward, (s_j, a_j, s_jp1) -> r_j
        r_j = None if tof_j is None else \
              util.get_reward(s_j, a_j, s_jp1, tof_j, tof_jp1)
        # and request an action for s_jp1 -> a_jp1
        # we also send back the previous reward to be used in experience replay
        a_jp1 = request_action(h.DQN_URL,  s_jp1, r_j)
        if a_jp1 is not None: driver.act(a_jp1)
        # once we've taken that action, move ahead a timestep
        s_j = s_jp1
        a_j = a_jp1
        tof_j = tof_jp1
        batch_update(h.DQN_URL, step_count)

        # delay to keep the loop frequency constant
        elapsed = time.time() - start
        delay = 1./h.FREQUENCY - elapsed
        if delay > 1e-4: camera.wait_recording(delay)
        else: print 1./elapsed
        step_count += 1
