from __future__ import print_function
from __future__ import division
from picamera import PiCamera
from time import sleep
from matplotlib import pyplot as plt
import cv2
import time
import argparse
import os
import imutils
from picamera.array import PiRGBArray
from picamera import PiCamera
from imutils.video import VideoStream
from imutils.video import FPS
from imutils import paths
from PIL import Image
import numpy as np;

#camera video setup
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
fps = FPS().start()
print("STARTING VIDEO FEED")

# LOOP CODE
while True: #constant video frame read
    frame = vs.read()
    
    #read image, rotate
#     pathname= os.path.join(directory, filename)
#     im=cv2.imread(pathname)
#     im = cv2.rotate(im, cv2.ROTATE_180)
    
    #convert to HSV, set HSV boundaries
    hsv=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
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
#         M = cv2.moments(c)
#         center=(int(M["m10"]/M["m00"]),int(M["m01"]/M["m00"]))
#         #drawing here:
        cv2.circle(frame, (int(x), int(y)), int(radius), (255,0,0), 2) #BOUNDING CIRCLE
#         cv2.circle(frame, center, 5, (255,0,0),-1) #CENTER
        
        
    #Photo dimensions: (1920,1080); Center coords: 960,540
    #Video Feed dimensions: (320,240); Center coords: 160,120
#     cx=160 #center x, photo: 960
#     cy=120 #center y, photo: 540
    imagesize=radius*2
#     u=x-cx
#     v=y-cy
#     v=-v #because reference frame is top left
#     cv2.circle(frame, (int(cx), int(cy)), 5, (0,0,255),-1) #drawing the image center point
    
    #calculate distance:
    physicalz=(imagesize/473)**(1/(-1.07))
#     #real life coords:
#     f=2714.29 #focal length in px
#     physicalx=(physicalz/f)*u
#     physicaly=(physicalz/f)*v

#     sizetext=imagesize, " px wide"
#     print(sizetext)
    cv2.putText(frame, str(imagesize), (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0))
#     print("Image Size: ", str(imagesize), " Physical Distance (approx): ", str(physicalz))
          #, " (u,v): (", u, ",", v, ")", " Real (X,Y,Z): (", physicalx, ",", physicaly,",", physicalz, ")")
    #print("Center: (", str(x), ",",str(y),")")
    cv2.imshow("Frame", frame)
    key= cv2.waitKey(5)# & 0xFF
    
    #to exit stream
    if key == 27: #esc key #ord("q"):
        print("esc key pressed")
        break
    
    fps.update()

#Stream end protocol:
print("VIDEO FEED STOPPED")

cv2.destroyAllWindows()
vs.stop()
