import requests
import cPickle as pickle
import numpy as np

import util

REQUEST_URL = 'http://138.16.161.77:5000'
REQUEST_URL = 'http://localhost:5000'

def request_action(url, state):
    """
    :param state: (img, flow, sensor, motor) tuple
    """
    encoded = pickle.dumps(state)
    headers = {'content-type': 'text'}
    response = requests.post(url + "/request_action", data=encoded, headers=headers)
    return pickle.loads(response.content)

def add_memory(url, mem):
    """
    :param mem: ((s_t), a_t, r_t, (s_t+1))
    """
    assert len(mem) == 4
    encoded = pickle.dumps(mem)
    headers = {'content-type': 'text'}
    response = requests.post(url + "/add_memory", data=encoded, headers=headers)

def batch_update(url):
    requests.post(url + "/batch_update")

if __name__ == '__main__':
    #print request_action(REQUEST_URL, util.get_random_state())
    for i in xrange(1050):
        add_memory(REQUEST_URL, util.get_random_mem())
    batch_update(REQUEST_URL)
