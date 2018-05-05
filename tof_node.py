#!/usr/bin/env python

import rospy
from explorer_bot.msg import Lidars
from subprocess import Popen, PIPE
import numpy as np

if __name__ == '__main__':
    pub = rospy.Publisher('/tof', Lidars, queue_size=1)
    rospy.init_node('tof_node')
    rate = rospy.Rate(10) # 10hz
    print "opening"
    tof_process = Popen(['./tof_test'], stdout=PIPE, stderr=PIPE) # start the tof sensors 
    while not rospy.is_shutdown():
        data = Lidars()
        data.header.stamp = rospy.Time.now()
        try:
            raw_dists = tof_process.stdout.readline().strip()
            data.ranges = np.array([int(i) for i in raw_dists.split('\t')])/255.
            print data.ranges
            pub.publish(data)
        except:
            print raw_dists
