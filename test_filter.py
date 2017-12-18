
from __future__ import print_function

import numpy as np
import argparse
import cv2    
import csv
import os 

refPt = (0, 0)

def click_and_crop(event, x, y, flags, param):
	# grab references to the global variables
	global refPt, cropping, cropDOne
	if event == cv2.EVENT_LBUTTONDOWN:
		print('left button pressed')
	if event == cv2.EVENT_RBUTTONDOWN:
		print('right button pressed')
	if event == cv2.EVENT_MOUSEMOVE:
		refPt = (x, y)

def showResizeImg(img, name, waitMS, x, y, width=1280, height=720):
	(h,w) = img.shape[:2]
	try:
		r = min([float(width)/w, float(height)/h])
	except:
		return (0, 0)
	(w, h) = (int(r * w), int(r * h))

	img = cv2.resize(img, (w, h))
	cv2.imshow(name, img)
	cv2.moveWindow(name, x, y)
	key = cv2.waitKey(waitMS)

	return (r, w, h, key & 0xFF)

def threshold_img(img, method):
	if (method == 'adaptive'):
		thresholded = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 25, 15)
	elif (method == 'OTSU'):
		T, thresholded = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
	else:
		if (method != None):
			try:
				T = int(method)
			except:
				T = 128
		T, thresholded = cv2.threshold(img, T, 255, cv2.THRESH_BINARY_INV)
	return thresholded

def morphological_process(img, method, kernelSize):
	if (method == 'closing'):
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernelSize)
		closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
		return closing
	elif (method == 'erode'):
		eroded = cv2.erode(img, None, iterations=1)
		return eroded
	elif (method == 'dilate'):
		dilated = cv2.dilate(eroded, None, iterations=1)
		return dilated
	return img.copy()	

def blur_img(img, method):
	if (method == 'bilateral'):
		diameter = 9
		sigmaColor = 21
		sigmaSpace = 7
		blur = cv2.bilateralFilter(img, diameter, sigmaColor, sigmaSpace)
	else:
		blur = img.copy()
	return blur	

def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-p", "--path", required=True, help="Path to the image")
	args = vars(ap.parse_args())

	cv2.namedWindow("image")

	f = open(args['path']+'/'+'color.csv', 'rb')
	reader = csv.reader(f, delimiter=' ',quoting=csv.QUOTE_MINIMAL)
	lowerColor, upperColor = next(reader)

	lowerColor = lowerColor.translate(None, '[],').split()
	lowerColor = [int(v) for v in lowerColor]

	upperColor = upperColor.translate(None, '[],').split()
	upperColor = [int(v) for v in upperColor]

	print('color = {}, {}'.format(lowerColor[0], upperColor[0]))
	f.close()	

	imageList = [ args['path']+'/'+f for f in os.listdir(args['path']) if f.endswith(".jpg") or f.endswith(".png") ]
	for imgName in imageList:
		img = cv2.imread(imgName)
		hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		showResizeImg(img, imgName, 0, 0, 0)
		mask = cv2.inRange(hsv, np.array(lowerColor, dtype='uint8'), np.array(upperColor, dtype='uint8'))
		showResizeImg(mask, 'filter mask', 0, 900, 0)

		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		thresholded = threshold_img(gray, 'adaptive')
		showResizeImg(thresholded, 'adaptive', 0, 900, 0)

		mixed_mask = cv2.bitwise_and(thresholded, thresholded, mask=mask)
		showResizeImg(mixed_mask, 'adaptive & color filter', 0, 900, 0)

		final = morphological_process(mixed_mask, 'closing', (7,7))
		
		(_, _, _, key) = showResizeImg(final, 'final', 0, 900, 0)


		cv2.destroyAllWindows()

		if key == ord('q'):
			break
	
main()