#Detect vansishing points in images of corridors
import cv2
import numpy as np
import points_average as pavg
import imutils
# Create a full screen window for viewing the results
cv2.namedWindow('Window', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('Window', cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)

# Read and remove noise from the image 
img = cv2.imread('Corridor.jpg')
img_width = img.shape[1]
img_height = img.shape[0]
img = imutils.resize(img, width = img.shape[1])
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img_gray = cv2.medianBlur(img_gray,7)
img_gray = cv2.GaussianBlur(img_gray, (5,5), 0)

# Find image gradient along the y axis
sobely_64f = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1 , ksize = 3)
abs_sobelx64F = np.absolute(sobely_64f)
abs_sobelx64F = abs_sobelx64F/ abs_sobelx64F.max() * 255
sobely_8u = np.uint8(abs_sobelx64F)
y_grad_threshold = sobely_8u

# Find image gradient along the x axis
sobelx_64f = cv2.Sobel(img_gray, cv2.CV_64F,1,0,ksize = 3)
abs_sobelx = np.absolute(sobelx_64f)
sobelx_8u = np.uint8(abs_sobelx)

# Find gradient magnitude and direction
grad_magnitude = cv2.add(sobely_8u,sobelx_8u)
grad_directions = np.arctan2(sobely_8u, sobelx_8u)

# Threshold gradient image to process essential pixels only
grad_directions[y_grad_threshold < 20] = -np.pi
grad_directions[ np.absolute(grad_directions) > 70 * np.pi/180] = -np.pi
grad_directions_normalized = ((grad_directions*180/np.pi) + 180)/360
grad_directions_8u = np.uint8(grad_directions_normalized * 255)

# Apply Hough transform to find lines in an image
Grid_locations = []
lines = cv2.HoughLines(grad_directions_8u, 1, np.pi/180, 185)
distance = np.zeros(lines.shape[1])
angles = np.zeros(lines.shape[1])
i = 0
j =0
G_x = np.zeros([int(img.shape[1]/8)], dtype = int)
G_y = np.zeros([int(img.shape[1]/8)], dtype = int)
m1 = 0
c1 = 0
for rho_1, theta_1 in lines[0]:
    a = np.cos(theta_1)
    b = np.sin(theta_1)        
    angles[i] = theta_1
    distance[i] = rho_1
    i+=1
    x0 = rho_1 * a
    y0 = rho_1 * b
    x1 = int(x0 + np.sqrt(np.square(img.shape[0]) + np.square(img.shape[1]))*(-b))
    y1 = int(y0 + np.sqrt(np.square(img.shape[0])+ np.square(img.shape[1]))*(a))
    x2 = int(x0 - np.sqrt(np.square(img.shape[0]) + np.square(img.shape[1]))*(-b)) 
    y2 = int(y0 - np.sqrt(np.square(img.shape[0]) + np.square(img.shape[1]))*(a))
    m2 = (float(y2 - y1)/(x2 - x1))
    c2 = y2 - m2*x2 
    if (m1 - m2)!=0:
        G_x[j] = int((c2 - c1)/(m1 - m2))
        G_y[j] = int(m2 * G_x[j] + c2)    
    Grid_locations.append((G_x[j],G_y[j]))  
    c1 = c2
    m1 = m2
    j+=1     
    cv2.line(img,(x2,y2),(x1,y1),(0,0,255),2)
    
Grid_locations = np.array(Grid_locations)
grid_xy = [15,15]
vanishing_point = pavg.vanishing_point(Grid_locations, img_width, img_height, grid_xy[0], grid_xy[1], 50)
vanishing_point = np.array(vanishing_point, dtype = int)
cv2.circle(img, (vanishing_point[0],vanishing_point[1]),int(img_width/50),(255,0,0),3)
cv2.imshow('Window',img)
k = cv2.waitKey(0) & 0xFF
if k == 27:
    cv2.destroyAllWindows()



