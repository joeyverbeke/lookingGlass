from __future__ import division
import Adafruit_PCA9685
import time
import zmq
import serial

timeLastSent = 0
timeBetweenSends = 50

ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)

sub.setsockopt(zmq.SUBSCRIBE, b'')
sub.connect(addr)

pan = 0
tilt = 0

pwm = Adafruit_PCA9685.PCA9685()

servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096

def set_servo_pulse(channel, pulse):
	pulse_length = 1000000    # 1,000,000 us per second
	pulse_length //= 60       # 60 Hz
	print('{0}us per period'.format(pulse_length))
	pulse_length //= 4096     # 12 bits of resolution
	print('{0}us per bit'.format(pulse_length))
	pulse *= 1000
	pulse //= pulse_length
	pwm.set_pwm(channel, 0, pulse)

def scaleNum(OldValue, OldMin, OldMax, NewMin, NewMax):
	return (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin

pwm.set_pwm_freq(60)

while True:
	headOffset = sub.recv_pyobj()
	camPan = int(180 - round(headOffset[0]))
	camTilt = int(round(headOffset[1]))

	pan = scaleNum(camPam, 0, 180, servo_min, servo_max)
	tilt = scaleNum(camTilt, 0, 180, servo_min, servo_max)

	print('pan: {}.'.format(pan))
	print('tilt: {}.'.format(tilt))

	if int(round(time.time() * 1000)) - timeLastSent > timeBetweenSends:
		pwm.set_pwm(0, 0, pan)
		timeLastSent = int(round(time.time() * 1000))

#	print('xOffset: {}.'.format(headOffset[0]))
#	print('yOffset: {}.'.format(headOffset[1]))
	print('---')
