from __future__ import division
import Adafruit_PCA9685
import time
import zmq

timeLastSent = 0
timeBetweenSends = 15

ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)

sub.connect("tcp://192.168.1.17:5555")
sub.setsockopt(zmq.SUBSCRIBE, b"")

#pan = 0
#tilt = 0

pwm = Adafruit_PCA9685.PCA9685()

servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096
servo_mid = 385

servoPan_pos = int(round(servo_min + (servo_max - servo_min)/2))
servoTilt_pos = int(round(servo_min + (servo_max - servo_min)/2))

#TODO: make a function of timeBetweenSends
servoPan_midBox = 10
servoPan_midBox_continuous = 25
servoTilt_midBox = 10

xOffset_max = 200
yOffset_max = 150

camPan_max = xOffset_max * 2
camTilt_max = yOffset_max * 2

#TODO: make a function of timeBetweenSends and midBoxes ???
panTilt_scaleDivisor = 20
continuousSpeedRange = 40


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

#TODO: make movement smoother, probably through smoother smaller grain steps
def setServoPos(yOffset):
        global servoTilt_pos

        if abs(yOffset) > (servo_max - servo_min) / servoTilt_midBox:
#	if True:
                if yOffset > 0:
                        tilt = scaleNum(yOffset, 0, camTilt_max/2, 0, yOffset_max / panTilt_scaleDivisor)
                        if (servoTilt_pos + tilt) < servo_max:
                                servoTilt_pos += tilt
                        else:
                                servoTilt_pos = servo_max
                elif yOffset < 0:
                        yOffset *= -1
                        tilt = scaleNum(yOffset, 0, camTilt_max/2, 0, yOffset_max / panTilt_scaleDivisor)
                        if (servoTilt_pos - tilt) > servo_min:
                                servoTilt_pos -= tilt
                        else:
                                servoTilt_pos = servo_min
        
'''
	global servoPan_pos

	if abs(xOffset) > (servo_max - servo_min) / servoPan_midBox:
#	if True:
		if xOffset > 0:
			pan = scaleNum(xOffset, 0, camPan_max/2, 0, xOffset_max / panTilt_scaleDivisor)
			if (servoPan_pos + pan) < servo_max:
				servoPan_pos += pan
			else:
				servoPan_pos = servo_max
		elif xOffset < 0:
			xOffset *= -1
			pan = scaleNum(xOffset, 0, camPan_max/2, 0, xOffset_max / panTilt_scaleDivisor)
			if (servoPan_pos - pan) > servo_min:
				servoPan_pos -= pan
			else:
				servoPan_pos = servo_min
'''

def setServoPos_continuous(xOffset):
	global servoPan_pos

	if abs(xOffset) > servoPan_midBox_continuous:
		if xOffset > 0:
			servoPan_pos = scaleNum(xOffset, 0, camPan_max/2, servo_mid, servo_mid + continuousSpeedRange) #(servo_max-servo_mid) / continousDivisor)
                        #servoPan_pos = 390
		elif xOffset < 0:
                        xOffset *= -1
                        pan = scaleNum(xOffset, 0, camPan_max/2, 0, continuousSpeedRange) #(servo_mid-servo_min) / continuousDivisor)
                        servoPan_pos = servo_mid - pan
                        #servoPan_pos = 380
	else:
		servoPan_pos = servo_mid

pwm.set_pwm_freq(60)

pwm.set_pwm(0, 0, servoPan_pos)
pwm.set_pwm(0, 0, servoTilt_pos)

while True:
	headOffset = sub.recv_pyobj()
	camPan = int(camPan_max - round(headOffset[0]))
	camTilt = int(round(headOffset[1]))

	pan = scaleNum(camPan, 0, camPan_max, servo_min, servo_max)
	tilt = scaleNum(camTilt, 0, camTilt_max, servo_min, servo_max)

#	print('pan: {}.'.format(camPan))
#	print('tilt: {}.'.format(camTilt))

	if int(round(time.time() * 1000)) - timeLastSent > timeBetweenSends:
		xOffset_inv = headOffset[0] * -1
		yOffset_inv = headOffset[1] * -1
		setServoPos_continuous(xOffset_inv)
		setServoPos(yOffset_inv)
		pwm.set_pwm(0, 0, int(round(servoPan_pos)))
		pwm.set_pwm(1, 0, int(round(servoTilt_pos)))
		print('servoPan_pos: {}.'.format(servoPan_pos))
		print('xOffset: {}.'.format(headOffset[0]))
		timeLastSent = int(round(time.time() * 1000))

#	print('---')
