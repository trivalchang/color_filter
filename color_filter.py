
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

def main():

	global bEnableDebug

	ap = argparse.ArgumentParser()
	ap.add_argument("-p", "--path", required=True, help="Path to the image")
	ap.add_argument("-t", "--threshold", required=False, default='adaptive', help='threshold method')
	ap.add_argument("-v", "--visualize", required=False, default=False, action='store_true', help='visualize the intermediate process')
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true', help='output debug info')
	args = vars(ap.parse_args())

	cv2.namedWindow("image")
	cv2.setMouseCallback("image", click_and_crop)

	img = cv2.imread(args['path'])
	#img = cv2.GaussianBlur(img,(11,11),0)
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	(ratio, winW, winH, _) = showResizeImg(img, 'image', 1, 0, 0)
	last = refPt
	s_lowerColor = [0, 0, 0]
	s_upperColor = [0, 0, 0]
	while (1):
		key = cv2.waitKey(1)
		if key == ord('q') or key == ord('f'):
			break

		if key == ord('t'):
			mask = cv2.inRange(hsv, min_color, max_color)
			showResizeImg(mask, 'mask', 1, 900, 0)
			s_lowerColor = min_color.flatten()
			s_upperColor = max_color.flatten()
			#final = cv2.bitwise_and(img, img, mask=mask)
			#final = cv2.cvtColor(final, cv2.COLOR_HSV2BGR)
			#showResizeImg(final, 'final {}-{}'.format(min_color, max_color), 1, 900, 0)


		if last == refPt:
			continue
		last = refPt
		(x, y) = tuple(int(float(p)/ratio) for p in refPt)
		print('ref = {}, [x, y]={}'.format(refPt, [x,y]))
		pick = img[y-winH/2:y+winH/2, x-winW/2:x+winW/2]
		showResizeImg(pick, 'image', 1, 0, 0, winW, winH)


		try:
			color = pick[refPt[1]-2:refPt[1]+2, refPt[0]-2:refPt[0]+2]
			color_hsv = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
			color_hsv = np.reshape(color_hsv, (16, 3))
			
		except:
			continue
	

		
		max_color = cv2.add(np.amax(color_hsv, axis=0), 30)
		min_color = cv2.subtract(np.amin(color_hsv, axis=0), 30)
		print('max = {}'.format(max_color))
		print('min = {}'.format(min_color))

		print('pick = {}'.format(pick[refPt[1], refPt[0]]))
		#showResizeImg(color, 'pick {}'.format(pick[refPt[1], refPt[0]]), 1, winW+20, 0, 20, 20)
	if key == ord('f'):
		f = open(os.path.dirname(args['path'])+'/color.csv', 'wb')
		writer=csv.writer(f, delimiter=' ',quoting=csv.QUOTE_MINIMAL)
		writer.writerow((s_lowerColor, s_upperColor))
		f.close()
	
main()