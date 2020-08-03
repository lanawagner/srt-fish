from __future__ import print_function
from __future__ import division
from picamera import PiCamera
from time import sleep
from matplotlib import pyplot as plt
import cv2
import argparse
import os
import imutils
from imutils import paths
from PIL import Image
import numpy as np;


# LOOP CODE
#reading all the files in crimages
directory = '/home/pi/Desktop/crimages/'
for filename in os.listdir(directory): #return filename + size
    
    #read image, rotate
    pathname= os.path.join(directory, filename)
    im=cv2.imread(pathname)
    im = cv2.rotate(im, cv2.ROTATE_180)
    
    #convert to HSV, set HSV boundaries
    hsv=cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    boundaries = [
        ([7,120,120], [153,255,255])#ORANGE, OpenCV measures HSV from 0-255 range
        #HSV in 0-100 range: [3,30,30], [60,100,100] #OLD: [7,76,76], [153,255,255]
    ]

    #cycling through boundaries, detecting mask
    for (lower,upper) in boundaries:
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")

        #HSV
        mask = cv2.inRange(hsv,lower,upper)
        output = cv2.bitwise_and(hsv,hsv, mask=mask)
        
    #finding contours
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    
    #largest contour, drawing bounding circle
    if len(cnts) > 0:
        c=max(cnts, key=cv2.contourArea)
        ((x,y),radius)= cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center=(int(M["m10"]/M["m00"]),int(M["m01"]/M["m00"]))
        cv2.circle(im, (int(x), int(y)), int(radius), (0,255,0), 2) #BOUNDING CIRCLE
        cv2.circle(im, center, 5, (255,0,0),-1) #CENTER
        
        
    cx=960 #center x
    cy=540 #center y
    imagesize=radius*2
    u=x-cx
    v=y-cy
    v=-v #because reference frame is top left
    cv2.circle(im, (int(cx), int(cy)), 5, (0,0,255),-1) #drawing the image center point
    
    #calculate distance:
    physicalz=(imagesize/2276)**(1/(-0.976))
    #real life coords:
    f=2714.29 #focal length in px
    physicalx=(physicalz/f)*u
    physicaly=(physicalz/f)*v
    
    print(pathname, " Image Size: ", str(imagesize), " Physical Distance: ", str(physicalz), " (u,v): (", u, ",", v, ")", " Real (X,Y,Z): (", physicalx, ",", physicaly,",", physicalz, ")")
    #print("Center: (", str(x), ",",str(y),")")
    cv2.imshow(pathname, im)
    cv2.waitKey(0)

#center coords: (960,540) (I THINK) (dimensions are (1920,1080)?)

