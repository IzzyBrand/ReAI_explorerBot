import requests
import grequests
import cPickle as pickle
import numpy as np

import util

REQUEST_URL = 'http://138.16.161.77:5000'
REQUEST_URL = 'http://localhost:5000'

def request_action(url, state, reward):
    """
    :param state: (img, flow, motor) tuple
    """
    encoded = pickle.dumps((state, previous_reward))
    headers = {'content-type': 'text'}
    response = requests.post(url + "/request_action", data=encoded, headers=headers)
    return pickle.loads(response.content)

def batch_update(url):
    req = grequests.post(url + "/batch_update")
    req.send()

if __name__ == '__main__':
    #print request_action(REQUEST_URL, util.get_random_state())
    batch_update(REQUEST_URL)
