import picamera
import picamera.array
import numpy as np

width = 80
height = 60

theGodArray = np.zeros([height,width,3, 1])

# Inherit from PiRGBAnalysis
class MyAnalysisClass(picamera.array.PiRGBAnalysis):
    def analyse(self, array):
        print('here')
        global theGodArray
        theGodArray = np.concatenate([theGodArray, np.expand_dims(array, axis=3)], axis=3)
        print theGodArray.shape


with picamera.PiCamera() as camera:
    with picamera.array.PiRGBAnalysis(camera) as output:
        camera.resolution = (width, height)
        camera.framerate = 15
        camera.vflip = True
        output = MyAnalysisClass(camera)
        camera.start_recording(output, format='rgb')
        camera.wait_recording(10)
        camera.stop_recording()

np.save('numpyVideo.npy', theGodArray)