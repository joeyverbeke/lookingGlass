from __future__ import division
import Adafruit_PCA9685
import time
import zmq

timeLastSent = 0
timeBetweenSends = 50

ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)

sub.connect("tcp://192.168.1.17:5555")
sub.setsockopt(zmq.SUBSCRIBE, b"")

pan = 0
tilt = 0

camPan_max = 400
camTilt_max = 300

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
	return int(round((((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin))

def moveAmount(facePos, _camTilt):
	if _camPa

pwm.set_pwm_freq(60)

while True:
	headOffset = sub.recv_pyobj()
	camPan = int(camPan_max - round(headOffset[0]))
	camTilt = int(round(headOffset[1]))

	pan = scaleNum(camPan, 0, camPan_max, servo_min, servo_max)
	tilt = scaleNum(camTilt, 0, camTilt_max, servo_min, servo_max)

	print('pan: {}.'.format(camPan))
	print('tilt: {}.'.format(camTilt))

	if int(round(time.time() * 1000)) - timeLastSent > timeBetweenSends:
		pwm.set_pwm(0, 0, pan)
		timeLastSent = int(round(time.time() * 1000))

	print('---')
