# Program to detect vanishing points in single images

import cv2
from Robust_may_13_tuning import HoughDetect_May_13
from Kalman_Filter import matrix
import time
import numpy as np

# Create a full screen window for viewing the results
cv2.namedWindow('Window', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('Window', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Read from Image
img = cv2.imread('Corridor.jpg')



# Image Resolution 
res = 1

# Inital state and covariance matrix
x = matrix([[960. * res],[330. * res]]) # 960, 330 are close to half of the original image height and width
P = matrix([[10000., 0.], [0., 10000.]])

count_hough = 0
t1 = []
while count_hough < 1:
	t0 = time.clock()
	img_result,x,P,measurement= HoughDetect_May_13(img,x,P,resolution = res)
	t1.append(time.clock() - t0)
	count_hough += 1

print 'Vanishing Point coordinates = {0}'.format(x)
print 'Img process time = {0} ms'.format(np.mean(t1) * 1000)


cv2.imshow('Window',img_result)
k = cv2.waitKey(0) & 0xFF

if k == ord('s'):
	cv2.imwrite('Corridor_slide_2.jpg', img_result)

if k == 27:      
	cv2.destroyAllWindows()