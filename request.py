import requests
import grequests
import cPickle as pickle
import numpy as np
import util
import hparams as hp
import sys
import time


def request_action(url, state, reward):
    """
    :param state: (img, flow, motor) tuple
    """
    encoded = pickle.dumps((state, reward))
    headers = {'content-type': 'text'}
    response = requests.post(url + "/request_action", data=encoded, headers=headers)
    return pickle.loads(response.content)

def batch_update(url, step_count):
    headers = {'content-type': 'text'}
    req = requests.post(url + "/batch_update", 
        data=str(step_count), headers=headers)
    #req.send()

if __name__ == '__main__':
    num_iters = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print 'Sending {} batch requests to {}'.format(num_iters, hp.DQN_URL)
    for i in range(num_iters):
        print 'Requesting update', i
        batch_update(hp.DQN_URL, i)
        time.sleep(1./hp.FREQUENCY)
