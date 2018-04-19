import os
import sys
import numpy as np

class Servo:
	def __init__(pins):
		self.pins = pins
		self.min = 1000
		self.mid = 1500
		self.max = 2000
		os.system('sudo servod --p1pins="{}"'.format(str(self.pins)[1:-1]))

	def write(servo_num, us):
		''' Write to a single servo in MicroSeconds mode. '''
		us = np.clip(us, self.min, self.max)
		os.system("echo {}={}us > /dev/servoblaster".format(servo_num, us))

	def multi_write(vals):
		''' Write to a all the servo in MicroSeconds mode. '''
		for servo_num, us in enumerate(np.clip(vals, self.min, self.max)):
			os.system("echo {}={}us > /dev/servoblaster".format(servo_num, us))

	def center_all():
		''' Writes all the servos to the midpoint value '''
		self.multi_write(np.ones_like(self.pins) * self.mid)


class Driver:
	def __init__(m1,m2):
		self.servo = Servo([m1,m2])

	def move(speed, turn):
		''' Move forward at `speed`, and rotate `turn`'''
		drive_1 = speed + turn
		drive_2 = speed - turn
		self.servo.multi_write()

	def stop():
		self.servo.center_all()


if __name__ == '__main__':
	if len(sys.argv < 3):
		print('python -i drive.py <m1Pin> <m2Pin>')
		sys.exit(1)

	d = Driver(int(sys.argv[1]), int(sys.argv[2])
