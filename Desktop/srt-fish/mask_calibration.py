import numpy as np
import argparse
import imutils
from imutils.video import VideoStream
from imutils.video import FPS
import time
import imutils
import cv2

#COLOR MASK CALIBRATION FOR OBJECT DETECTION FROM VIDEO FEED

#camera video setup
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
fps = FPS().start()
print("STARTING VIDEO FEED")

#convert to HSV, set HSV boundaries
boundaries = [
    ([7,120,120], [153,255,255]) #CHANGE THE MASK VALUES FOR CALIBRATION HERE
]

while True:
    frame = vs.read()

    hsv=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

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
        cv2.circle(output, (int(x), int(y)), int(radius), (0,255,0), 2) #BOUNDING CIRCLE
        
        
    #displaying mask and bounding circle
    cv2.imshow("mask", output)
    key= cv2.waitKey(5)# & 0xFF
        
    if key == 27: #esc key #ord("q"):
        print("esc key pressed")
        break
    
    fps.update()
        


print("VIDEO FEED STOPPED")

cv2.destroyAllWindows()
vs.stop()


#         cv2.waitKey(0)
#         
#     #finding contours
#     cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     cnts = imutils.grab_contours(cnts)
#     center = None
# 
#     #largest contour, drawing bounding circle
#     if len(cnts) > 0:
#         c=max(cnts, key=cv2.contourArea)
#         ((x,y),radius)= cv2.minEnclosingCircle(c)
#         M = cv2.moments(c)
#         center=(int(M["m10"]/M["m00"]),int(M["m01"]/M["m00"]))
#         cv2.circle(im, (int(x), int(y)), int(radius), (0,255,0), 2) #BOUNDING CIRCLE
#         cv2.circle(im, center, 5, (255,0,0),-1) #CENTER
# 
# #prints and display
# diameter=radius*2
# print("Diameter: ", str(diameter))
# print("Center: (", str(x), ",",str(y),")")
# cv2.imshow("Image", im)
# cv2.waitKey(0)