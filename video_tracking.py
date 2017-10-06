# Main Program to detect and track vanishing points in an image
#------------------------------------------------------------------------------------------------------------------------------#
import cv2
from Robust_may_13_tuning import HoughDetect_May_13
from Kalman_Filter import matrix
import time
import numpy as np
import matplotlib.pyplot as plt


# Timing information to compute algorithm runtime
t0 = time.clock()

# Create a full screen window for viewing the results
cv2.namedWindow('Window', 1)
cv2.setWindowProperty('Window', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Read from video object
cap = cv2.VideoCapture('Corridor_straight.mp4')

# Creat 'out'object for recording the result
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('test_perfect_vanishing.avi', fourcc, 20.0, (640,360))

frame_count = 0
feature = []
t1 = []
v_init_x = 0
v_init_y = 0

displacement = []

# Image Resolution 

# Decrease the resolution to speed up the algorithm, note that the threshold parameter in probabilistic Hough transform function must also be varied
# for the algorithm to detect enough lines at lower resolutiuons ) 

res = 1

# Inital state and covariance matrix
# The values 960 and 330 are approximately half and 1/3rd the i/p image width and height respectively
# This initalization depends on the problem you want to solve
# For tracking vp's in corridors, initalizing with 1/3rd the image height was convenient (led to faster tracking convergence)
x = matrix([[960. * res],[330. * res]]) 
# Intialize the inital uncertainty matrix to a large value  
P = matrix([[10000., 0.], [0., 10000.]])



print 'Number of frames = {0} '.format(cap.get(7))

while(cap.isOpened()):

    # Read frames from the video object 
    ret,img = cap.read()
    frame_count+=1
    
    # Pass frame to line detection module
    img_result,x,P,measurements= HoughDetect_May_13(img,x,P,resolution = res)
    out.write(img_result)

    
    print 'Vanishing Point coordinates = {0}'.format(x)
    cv2.imshow('Window',img_result)
    k = cv2.waitKey(1) & 0xFF

    # Press ESC to stop the program
    if k == 27 or frame_count == cap.get(7) :   
        t1 = time.clock() - t0
        ctime = t1/frame_count
        cap.release()
        break


cv2.destroyAllWindows()
print ctime

        
            
                
                    
                            