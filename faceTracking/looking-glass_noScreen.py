# USAGE
# python looking-glass_noScreen.py --prototxt deploy.prototxt.txt --model res10_300x300_ssd_iter_140000.caffemodel

# import the necessary packages
from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import time
import cv2
import zmq
import sys

addr = 'tcp://192.168.1.17:5555'
ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind(addr)
time.sleep(1.0)

biggestFace = 0
biggestFaceIndex = 0
faces = []

timeFaceLost = 0
trackingFace = False
stopMovingTimeThreshold = 1000
timeFaceFound = 0
possibleFaceFound = False
startTrackingTimeThreshold = 500

sendAsPantTilt = False

def scaleValue(old, oldMin, oldMax, newMin, newMax):
	scaledVal = (((old - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) + newMin
	return scaledVal

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream and allow the cammera sensor to warmup
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

#TODO: add in sigint intercept

recName = '/home/seph/Desktop/lookingGlass/faceTracking/recordings/'
recName += str(int(round(time.time() * 1000)))
recName += ".avi"
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
recording = cv2.VideoWriter(recName, fourcc, 30.0, (400, 300))

# loop over the frames from the video stream
while True:
	try:

		frame = vs.read()

		#write to disk
		recFrame = imutils.resize(frame, height=300)
		#print("length: {}.".format(len(recFrame.shape)))
		#print("width: {}.".format(recFrame.shape[0]))
		#print("height: {}.".format(recFrame.shape[1]))
		recording.write(recFrame)

		frame = imutils.resize(frame, width=400)


		# grab the frame dimensions and convert it to a blob
		(h, w) = frame.shape[:2]
		blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
			(300, 300), (104.0, 177.0, 123.0))

		# pass the blob through the network and obtain the detections and
		# predictions
		net.setInput(blob)
		detections = net.forward()

		# loop over the detections
		for i in range(0, detections.shape[2]):
			# extract the confidence (i150.e., probability) associated with the
			# prediction
			confidence = detections[0, 0, i, 2]

			# filter out weak detections by ensuring the `confidence` is
			# greater than the minimum confidence
			if confidence < args["confidence"]:
				continue

			# compute the (x, y)-coordinates of the bounding box for the
			# object
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			frameWidth = w
			frameHeight = h

			middleX = startX + (endX - startX)/2
			middleY = startY + (endY - startY)/2

			boxSize = (endX - startX) * (endY - startY)

			if endX > frameWidth or endY > frameHeight: #if valid face
				break
				if biggestFaceIndex < boxSize: #if biggest face
					biggestFace = boxSize
					biggestFaceIndex = i

			xOffset = middleX - w/2
			yOffset = middleY - h/2

			if possibleFaceFound is False:
				timeFaceFound = int(round(time.time() * 1000))
				possibleFaceFound = True

			if timeFaceFound is not 0 and int(round(time.time() * 1000)) - timeFaceFound > startTrackingTimeThreshold:
				faces.append([xOffset,yOffset])
				trackingFace = True
			else:
				print("face found for: {}.".format(int(round(time.time() * 1000)) - timeFaceFound))

			#pub.send_pyobj([xOffset, yOffset])

			#print("startX: {}.".format(startX))
			#print("startY: {}.".format(startY))
			#print("endX: {}.".format(endX))
			#print("endY: {}.".format(endY))
			#print("middleX: {}.".format(middleX))
			#print("middleY: {}.".format(middleY))
			#print("xOffset: {}.".format(xOffset))
			#print("yOffset: {}.".format(yOffset))
			#print("")

			# draw the bounding box of the face along with the associated
			# probability
			text = "{:.2f}%".format(confidence * 100)
			y = startY - 10 if startY - 10 > 10 else startY + 10
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				(0, 0, 255), 2)
			cv2.putText(frame, text, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
		if len(faces) > 0:
			print("xOffset: {}.".format(faces[biggestFaceIndex][0]))
			print("yOffset: {}.".format(faces[biggestFaceIndex][1]))
			print('---')

			if trackingFace:
				if sendAsPantTilt:
					panVal = scaleValue(faces[biggestFaceIndex][0], -200, 200, 0, 400)
					tiltVal = scaleValue(faces[biggestFaceIndex][1], -150, 150, 0, 300)
					panTilt = [panVal, tiltVal]
					pub.send_pyobj(panTilt)
				else:
					pub.send_pyobj(faces[biggestFaceIndex])
			else:
				pub.send_pyobj(['d', 'd'])

			biggestFace = 0
			biggestFaceIndex = 0
			faces = []
		else:
			if trackingFace == True:
				trackingFace = False
				timeFaceLost = int(round(time.time() * 1000))
				timeFaceFound = 0
				possibleFaceFound = False
				#print('starting default anim')
			if int(round(time.time() * 1000)) - timeFaceLost > stopMovingTimeThreshold:
				#print("default")
				pub.send_pyobj(['d','d'])


		# show the output frame
		#cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break
	except KeyboardInterrupt:
		# do a bit of cleanup
		cv2.destroyAllWindows()
		vs.stop()
		recording.release()
		print("byeBye")
		sys.exit()


# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
recording.release()
