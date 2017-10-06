# Vanishing_point
Detects vanishing points in an image

Parallel lines, not perpendicular to the plane of the camera, intersect at a point as a consequnce of perspective projection. 
The intersection point may not always be in the image plane. This module attempts to detect such an intersection point (vanishing point) 
in an indoor setting (corridor).

<p align="center">
  <img width="460" height="300" src="./img_pipeline_1.jpg">
</p>
<p align="center">
  <img width="460" height="300" src="./img_pipeline_2.jpg">
</p>
<p align="center">
  <img width="460" height="300" src="./img_pipeline_3.jpg">
</p>
<p align="center">
  <img width="460" height="300" src="./img_pipeline_4.jpg">
</p>
<p align="center">
  <img width="460" height="300" src="./img_pipeline_5.jpg">
</p>

# Setup Instructions
The file Single_image_test.py takes in an input image and determines the median vanishing point estimated by computing the intersection point of several detected line segements. Make sure you download the relevant dependencies: 'Robust_may_13_tuning.py', 'Kalman_Filter.py', 'intersecion_library.py'

For using the algorithm to track vanishing point across frames, look at the format of the video_tracking.py file. The blue circle indicates the vanishing point estimated from measurement and the green circle indicates the vanishing point estimated by the State Estimation filter (EKF). The two images below represent consecutive image frames, notice how the lack of prominent lines disrupts the measurment estimate (represented by the blue circle) on the RHS image but the EKF estimate (represented by the green circle) hold steady in the face of uncertainty.
![alt-text-1](./EKF_1.png) ![alt-text-2](./EKF_2.png)



