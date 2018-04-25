import picamera
import picamera.array
import numpy as np
import io
import socket
import pickle


class FrameAnalyzer(picamera.array.PiRGBAnalysis):
    def setup(self, filename):
        self.file = open(filename, 'ab')

    def analyse(self, array):
        pickle.dump(array, self.file)

    def close(self):
        self.file.close()


class FlowAnalyzer(picamera.array.PiMotionAnalysis):
    def setup(self, filename):
        self.file = open(filename, 'ab')

    def analyse(self, array):
        x = array['x']
        y = array['x']
        pickle.dump(array, self.file)

    def close(self):
        self.file.close()


if __name__ == '__main__':
    with picamera.PiCamera(framerate=90) as camera:
        camera.resolution = (320, 240)
        with FrameAnalyzer(camera) as frame_analyzer:
            with FlowAnalyzer(camera) as flow_analyzer:
                frame_analyzer.setup('frame.pkl')
                flow_analyzer.setup('flow.pkl')
                # start the recordings for the image and the motion vectors
                camera.start_recording("/dev/null", format='h264', splitter_port=1, motion_output=flow_analyzer)
                camera.start_recording(frame_analyzer, format='bgr', splitter_port=2)
                 # nonblocking wait
                camera.wait_recording(5)

                camera.stop_recording(splitter_port=1)  # stop recording both the flow 
                camera.stop_recording(splitter_port=2)  # and the images


