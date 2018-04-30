import requests
import cPickle as pickle
import numpy as np

REQUEST_URL = 'http://localhost:5000/action'

def request_action(cam_img, flow_img, lidar_data, motor_speeds):
    info_dict = {
        'cam': cam_img,
        'flow': flow_img,
        'lidar': lidar_data,
        'motor': motor_speeds
    }
    encoded = pickle.dumps(info_dict)
    headers = {'content-type': 'text'}
    response = requests.post(REQUEST_URL, data=encoded, headers=headers)
    return pickle.loads(response.content)

if __name__ == '__main__':
    cam = np.random.random((100, 100, 3))
    flow = np.random.random((100, 100, 3))
    lidar = np.random.random((4,))
    motor = np.random.random((2,))
    print request_action(cam, flow, lidar, motor)
