import os
import sys
import numpy as np
import util

class Servo:
	def __init__(self, pins):
		self.pins = pins
		self.min = 1000
		self.mid = 1500
		self.max = 2000
		os.system('sudo servod --p1pins="{}"'.format(str(self.pins)[1:-1]))

	def write(self, servo_num, us):
		''' Write to a single servo in MicroSeconds mode. '''
		us = np.clip(us, self.min, self.max)
		os.system("echo {}={}us > /dev/servoblaster".format(servo_num, us))

	def multi_write(self, vals):
		''' Write to a all the servo in MicroSeconds mode. '''
		for servo_num, us in enumerate(np.clip(vals, self.min, self.max)):
			os.system("echo {}={}us > /dev/servoblaster".format(servo_num, us))

	def center_all(self):
		''' Writes all the servos to the midpoint value '''
		self.multi_write(np.ones_like(self.pins) * self.mid)

	def close(self):
		os.system("sudo killall servod")

class Driver:
	def __init__(self, m1,m2):
	    self.servo = Servo([m1,m2])
	    self.mid = 1500
	    self.m = np.array([self.mid, self.mid])

	def move(self, speed, turn):
	    ''' Move forward at `speed`, and rotate `turn`'''
	    self.m = np.array([-speed, speed]) + self.mid + turn
	    self.servo.multi_write([self.m])

	def stop(self):
            self.move(0,0)

	def dmotor(self, d):
	    ''' Delta the motor speeds by the specified amounts '''
            self.m = np.clip(self.m + d, 1000, 2000)
	    self.servo.multi_write(self.m)

	def get_motor(self):
		''' get the motor speeds normalized -1 to 1 '''
		return (self.m - 1000)/500.

	def act(self, action):
		self.dmotor(util.action_to_motor(action))

	def close(self):
		self.stop()
		self.servo.close()


if __name__ == '__main__':
	if len(sys.argv) < 3:
		print('python -i drive.py <m1Pin> <m2Pin>')
		sys.exit(1)

	d = Driver(int(sys.argv[1]), int(sys.argv[2]))
