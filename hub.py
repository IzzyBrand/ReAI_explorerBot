import picamera
import numpy as np
import pickle
from drive import Driver


class FrameAnalyzer(picamera.array.PiRGBAnalysis):
    def setup(self, filename=None):
        if filname is not None: self.file = open(filename, 'ab')
        else: self.file = None

    def analyse(self, array):
        self.array = array
        if self.file is not None: pickle.dump(array, self.file)

    def close(self):
        if self.file is not None: self.file.close()


class FlowAnalyzer(picamera.array.PiMotionAnalysis):
    def setup(self, filename=None):
        if filname is not None: self.file = open(filename, 'ab')
        else: self.file = None

    def analyse(self, array):
        self.array = array
        if self.file is not None: pickle.dump(array, self.file)

    def close(self):
        if self.file is not None: self.file.close()

functions_to_call_on_exit = []

# kill a bunch of things on exit
def signal_handler(signal, frame):
        for f in functions_to_call_on_exit: f()
        sys.exit(0)


framerate = 15
width, height = 160, 120

if __name__ == '__main__':
    ########################### INIT THE TOF SENSOR ########################### 
    # TODO: Initialize threading module to read from the TOF sensor

    ############################# INIT THE DRIVER ############################# 
    driver = Driver(12,18)
    function_to_call_on_exit.append(driver.stop)

    ############################# INIT THE CAMERA ############################# 
    signal.signal(signal.SIGINT, signal_handler)
    camera = picamera.PiCamera(framerate=90):
    camera.resolution = (width, height)
    frame = FrameAnalyzer(camera)
    flow = FlowAnalyzer(camera)
    frame.setup('frame.pkl')
    flow.setup('flow.pkl')
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
    while True:
        print(frame.data.shape, flow.data.shape)
        driver.stop()



