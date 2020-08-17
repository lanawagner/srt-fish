from collections import deque
from picamera import PiCamera
import cv2
import time
import argparse
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

ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
args = vars(ap.parse_args())

#ORANGE COLOR MASK:
boundaries = [
    ([7,120,120], [153,255,255])#ORANGE, OpenCV measures HSV from 0-255 range
    #HSV in 0-100 range: [3,30,30], [60,100,100] #OLD: [7,76,76], [153,255,255]
]

#TRACKED POINTS:
pts=deque(maxlen=args["buffer"])

# LOOP CODE
while True: #constant video frame read
    frame = vs.read()
    
    #convert to HSV, set HSV boundaries
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
        #detecting ball and center:
        c=max(cnts, key=cv2.contourArea)
        ((x,y),radius)= cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        if M==0: #to fix the divide by zero error?
            cv2.putText(frame, "ERROR, no center", (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0))
            break
        center=(int(M["m10"]/M["m00"]),int(M["m01"]/M["m00"]))
        
        #drawing here:
        cv2.circle(frame, (int(x), int(y)), int(radius), (255,0,0), 2) #BOUNDING CIRCLE (blue)
        cv2.circle(frame, center, 5, (0,255,0),-1) #CENTER (green)
        
        diameter=radius*2
        
        #calculate z distance:
        zcoord=(diameter/473)**(1/(-1.07))
        physicalz= "Z: " + str(zcoord) + " in"
        #cv2.putText(frame, str(physicalz), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0))
        
        #calculating u and v coordinates:
            #Photo dimensions: (1920,1080); Center coords: 960,540
            #Video Feed dimensions: (320,240); Center coords: 160,120
        cx=160 #video center x, photo: 960
        cy=120 #video center y, photo: 540
        u=x-cx
        v=y-cy
        v=-v #because reference frame is top left
        
        f=2714.285714 #focal length in px
        xcoord=(zcoord/f)*u
        ycoord=(zcoord/f)*v
        
        #truncating floats:
        u='%.2f'%(u)
        v='%.2f'%(v)
        xcoord='%.2f'%(xcoord)
        ycoord='%.2f'%(ycoord)
        zcoord='%.2f'%(zcoord)
        diameter='%.2f'%(diameter)
        
        imagesize=str(diameter) + " px wide"
        cv2.putText(frame, str(imagesize), (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0))
        
        uvcoord="(u,v): (" + str(u) + "," + str(v) + ")"
        cv2.circle(frame, (int(cx), int(cy)), 5, (0,0,255),-1) #drawing the image center point
        cv2.putText(frame, str(uvcoord), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,25))
        
        realcoords="(X,Y,Z): (" + str(xcoord) + "," + str(ycoord)  + "," + str(zcoord) + ")"
        cv2.putText(frame, str(realcoords), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0))
        
        pts.appendleft(center) #THIS USED TO NOT BE INDENTED, CHECK IF IT'S STILL OK
    
    else:
        cv2.putText(frame, "object not found", (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0))
    
    for i in range(1, len(pts)):
        if pts[i-1] is None or pts[i] is None:
            continue
        #thickness = int(np.sqrt(args["buffer"]/float(i+1))*2.5)
        cv2.line(frame, pts[i-1],pts[i],(0,0,255), 1)
    
    #displaying video feed:
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
