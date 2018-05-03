import os
import sys
import numpy as np

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
		self.drive_m1 = self.mid
		self.drive_m2 = self.mid

	def move(self, speed, turn):
		''' Move forward at `speed`, and rotate `turn`'''
		self.drive_m1 = self.mid - speed + turn
		self.drive_m2 = self.mid + speed + turn
		self.servo.multi_write([self.drive_m1, self.drive_m2])

	def stop(self):
		self.move(0,0)

	def dfb(self,speed):
		self.drive_m1 -= speed 
		self.drive_m2 += speed
		self.servo.multi_write([self.drive_m1, self.drive_m2])

	def close(self):
		self.stop()
		self.servo.close()


if __name__ == '__main__':
	if len(sys.argv) < 3:
		print('python -i drive.py <m1Pin> <m2Pin>')
		sys.exit(1)

	d = Driver(int(sys.argv[1]), int(sys.argv[2]))
