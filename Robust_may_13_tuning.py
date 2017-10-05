# Program to extract lines in an image using probabilistic Hough transform

import time
import cv2
import imutils
import numpy as np
from Kalman_Filter import matrix
from Kalman_Filter import EKF
import intersection_library


def HoughDetect_May_13(img,x,P,resolution = 1):

    # img : Input Image
    # x : Intial Vanishing Point Coordinates. It is of type Matrix (See Kalman_filter.py)
    # P : Uncertainty Matrix
    # Resolution : Image resolution, set to actual resolution of input image by default. 

  
    i_x = x.value[0][0] # x-coordinate of the vanishing point
    i_y = x.value[1][0]  # y-coordinate of the vanishing point
    i_w = int(img.shape[1] * resolution) # image width 
    img = imutils.resize(img, width = i_w) # resizing image for desired resolution
    i_h = int(img.shape[0]) # image height
    print "Image Width = {0}, Image Height  = {0}".format(i_w,i_h) # Comment if running on a video file

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # BGR TO GRAYSCALE
    img_gray = cv2.medianBlur(img_gray,3) # Removes salt and pepper noise by convolving the image with a (3,3) square kernel
    img_gray = cv2.GaussianBlur(img_gray, (9,9), 0)  # Smoothens the image by convolving the with a (9,9) Gaussian filter 
    

    # Find Image Gradient along the Y-axis
    sobely_64f = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1 , ksize = 3) # Sobel filter size:(3,3)
    abs_sobelx64F = np.absolute(sobely_64f)
    abs_sobelx64F = abs_sobelx64F/ abs_sobelx64F.max() * 255 # Force pixel values to be in range [0, 255] 
    sobely_8u = np.uint8(abs_sobelx64F) # Force pixels to take integer values
    y_grad_threshold = sobely_8u.copy() # Make a copy for further thresholding 
    

    # Find Image Gradient along the X-axis
    sobelx_64f = cv2.Sobel(img_gray, cv2.CV_64F, 1 , 0,ksize = 3) # Sobel filter size: (3,3)
    abs_sobelx = np.absolute(sobelx_64f)
    abs_sobelx = abs_sobelx/abs_sobelx.max() *  255 # Force pixel values to be in range [0, 255]
    sobelx_8u = np.uint8(abs_sobelx)


    # Find gradient direction
    grad_directions = np.arctan2(sobely_8u, sobelx_8u) 


    # Threshold gradient direction image to process essential pixels only
    y_grad_threshold[y_grad_threshold > 30] = 255
    grad_directions[y_grad_threshold < 10] = -np.pi 
    grad_directions_normalized = ((grad_directions*180/np.pi) + 180)/360 # Force pixels to be in range [0,1]
    grad_directions_8u = np.uint8(grad_directions_normalized * 255) # Rescale pixels to lie in [0, 255]
    

    # Hough Transform
    maxLineGap = 2 # max pixel spacing between 2 lines for it to be considered 1 line
    adaptive = int(100*resolution) # Needs to be decreased as the resolution is decreased
    minLineLength = adaptive # Min length of line in pixels to be extracted

    # Use the probabilistic Hough Transform with 'rho' value of 1 pixel and 'theta' value of 1 degree
    # The values of 'rho' and 'theta' represent the granularity of the detection scheme (rho = 1 means check every pixel, theta =  1 degree means check for every 1 degree variation) and 
    # determine the dimensions of the Hough accumulator array (please see OpenCV Hough Transform for more details) 
    # You can speed up line detection (by sacrificing for accuracy) by increasing the rho and theta values     
    # The probabilistic Hough transform randomly samples sections of the image for lines (this only works if the image is structurally rich). 
    # The output is a list in which every element describes a line by its end points (x1,y1) and (x2,y2) 
    lines = cv2.HoughLinesP(grad_directions_8u,1,np.pi/180,400,minLineLength,maxLineGap) # Threshold of 400 needs to be decreased with image resolution


        
    # Intailizing empty lists
    lines_new = []
    lines_EKF = []
    lines_inter = []
    lines_r_l = []

    # Yellow line to visualize vanishing point change with lateral camera movement
    cv2.line(img,(0,int(i_h/(3))),(i_w,int(i_h/(3))),(0,255,255),2)



    # Select lines that satisfy application constraints (detecting lines ina an indoor corridor)
   
    if lines is not None: 
        for feature in range(len(lines)):
            for x1,y1,x2,y2 in lines[feature]:
                if (x1- x2)!=0: # Make sure lines are not collinear 
                    theta = np.arctan2((y2-y1),(x2-x1))
                    m2= np.tan(theta)
                    l_mag = np.sqrt(np.square(x1 - x2) + np.square(y1 - y2))

                    # Extend the lines to the entire image and compute the intersetion point
                    c2 = y1 - m2*x1
                    x3 = int(1000 + x1) # 1000 was chosen arbitrarily (any number higher than half the image width) 
                    y3 = int(m2*x3 + c2)
                    x4 = int(x1 - 1000) # 1000 was chosen arbitrarily 
                    y4 = int(m2*x4 + c2)

                    if abs(theta) > 0.1 and l_mag > 20  and abs(theta) < 1.3: # Eliminate short lines and lines that are close to being perfectly horizontal or vertical
                        lines_EKF.append((x1,y1))
                        lines_r_l.append((x1,y1,x2,y2))
                        cv2.line(img,(x3,y3),(x4,y4),(0,0,255),3)                        
                    
                      
    else:
        return img,x,P,x # Since there were no measurement for this frame, return state info twice
    
    

    # Computer the Homogenous representation of the lines given the detected end points 
    if len(lines_r_l)!=0:
        lines_all = intersection_library.lines_from_points(lines_r_l)
      
        for j in range(len(lines_all) - 1):
            for k in range(j+1, len(lines_all)):
                lines_inter.append((lines_all[j], lines_all[k]))


    # Compute the intersection point of all the lines
    if len(lines_inter) != 0:
        i_x,i_y = intersection_library.points_from_lines(lines_inter, x)    

    # Draw a  blue circle around the measurment point given by x axis of the interction point and 1/3 rd of the image height.
    # This is done to highlight changes in the horizontal position of the Vanishing point as that it what we are interested in.
        cv2.circle(img,(i_x,int(i_h/3)) ,int(i_w/50),(255,0,0),3)


    # Passing measurment information to the State Estimation Filter (EKF) 
    lines_new = np.array(lines_EKF)
    measurements = matrix([[i_x],[i_y]])
    x,P = EKF(x,P,lines_new,measurements,resolution)
    v_1 = int(x.value[0][0])
    v_2 = int(x.value[1][0])

    # Draw a green circle around the vanishing point estimated by the EKF
    cv2.circle(img,(v_1,int(i_h/3)) ,int(i_w/48),(0,255,0),3)


    return img,x,P,measurements
   

