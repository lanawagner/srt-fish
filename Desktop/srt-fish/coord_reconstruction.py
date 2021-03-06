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
from imutils.video import count_frames
from imutils import paths
from PIL import Image
import numpy as np;

#camera video setup
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
# fps = FPS().start()
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

#frame counter:
framenumber=0

(dX, dY) = (0,0)
direction = ""


# LOOP CODE
while True: #constant video frame read
    frame = vs.read()
    fps = FPS().start()
    
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
        if (M["m00"]==0): #to fix the divide by zero error?
            cv2.putText(frame, "ERROR, no center", (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0))
        else:
            center=(int(M["m10"]/M["m00"]),int(M["m01"]/M["m00"]))
        
        #drawing here:
        cv2.circle(frame, (int(x), int(y)), int(radius), (255,0,0), 2) #BOUNDING CIRCLE (blue)
        cv2.circle(frame, center, 5, (0,255,0),-1) #CENTER (green)
        
        diameter=radius*2
        
        #calculate z distance:
        zcoord=(diameter/473)**(1/(-1.07))
        #cv2.putText(frame, str(physicalz), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0))
        
        #calculating u and v coordinates:
            #Photo dimensions: (1920,1080); Center coords: 960,540
            #Video Feed dimensions: (320,240); Center coords: 160,120
        cx=160 #video center x, photo: 960
        cy=120 #video center y, photo: 540
        u=x-cx
        v=y-cy
        v=-v #because reference frame is top left
        
        f=252
        #OLD: f=2714.285714 #focal length in px
        xcoord=(zcoord/f)*u
        ycoord=(zcoord/f)*v
        #convert to cm:
        zcoord=zcoord*(2.54)
        physicalz= "Z: " + str(zcoord) + " m"
        xcoord=xcoord*2.54
        ycoord=ycoord*2.54
        
        #truncating floats:
        u='%.2f'%(u)
        v='%.2f'%(v)
        xcoord='%.2f'%(xcoord)
        ycoord='%.2f'%(ycoord)
        zcoord='%.2f'%(zcoord)
        diameter='%.2f'%(diameter)
        
        uvcoord="(u,v): (" + str(u) + "," + str(v) + ")"
        cv2.circle(frame, (int(cx), int(cy)), 5, (0,0,255),-1) #drawing the image center point
        cv2.putText(frame, str(uvcoord), (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,25))
        
        realcoords="(X,Y,Z): (" + str(xcoord) + "," + str(ycoord)  + "," + str(zcoord) + ")"
        cv2.putText(frame, str(realcoords), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0))
        
        pts.appendleft(center)
        

    else:
        cv2.putText(frame, "object not found", (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0))
    
#     sumposx=0
#     sumposy=0
    #drawing tail and determining direction (and later velocity)
    for i in np.arange(1, len(pts)):
#         #TEST: smoothing function
#         sumposx=sumposx+pts[i][0]
#         sumposy=sumposy+pts[i][1]
        
        
        if pts[i-1] is None or pts[i] is None:
            continue
        
        if framenumber >= 10 and i == 1 and len(pts) == args["buffer"]: #pts[i-10] is not None:
            #determine direction
            dX = pts[i][0]-pts[i-1][0]
            dY = pts[i][1]-pts[i-1][1]
            (dirX, dirY) = ("", "")
            far=""
            swimspeed=""
            
            #determine FPS
            fps.update()
            fps.stop()
            framerate= fps.fps()
            
            d=radius*2
            zdist=(d/473)**(1/(-1.07))
            
            #buffer to get rid of small movements (only big changes in position)
            if np.abs(dX)>=10:
                #calculating velocities, cleaning up strings
                #currently in px/s
                xvelocity=(pts[i][0]-pts[i-1][0])*framerate
                xvelocity=xvelocity*(zdist/f)
                xvelocity=xvelocity*.0254
                
                xvelocity='%.2f'%(xvelocity)
                v_x="V(x)= " + str(xvelocity) + "m/s"
                cv2.putText(frame, str(v_x), (0,80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0))
                
            if np.abs(dY)>=10:
                yvelocity=(pts[i][1]-pts[i-1][1])*framerate
                yvelocity=yvelocity*(zdist/f)
                yvelocity=yvelocity*.0254
                
                yvelocity='%.2f'%(yvelocity)
                v_y="V(y)= " + str(yvelocity) + "m/s"
                cv2.putText(frame, str(v_y), (0,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0))
    
            #object location cases
                #FIGURE OUT WHY ALWAYS UP AND RIGHT
            if pts[i][0]-cx>0:
                dirX= "right"
            else:
                dirX="left"
                
            if pts[i][1]-cy>0:
                dirY= "down"
            else:
                dirY= "up"
                    
            if 0<=zdist<=12:
                far="close"
                swimspeed="slow"
            
            elif 12<zdist<=36:
                far="medium"
                swimspeed="medium"
            
            else:
                far="far away"
                swimspeed="fast"
                
            if dirX != "" and dirY != "":
                direction = dirY + " and " + dirX
                
            else:
                direction = dirX if dirX != "" else dirY
                
            swiminstructions="object: " + far + ", swim " + direction + " at " + swimspeed + " speed"
        
            #writing direction
            cv2.putText(frame, swiminstructions, (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0))
        
#         #calculating smoothed position??????
#         smoothposx=sumposx/(len(pts))
#         smoothposy=sumposy/(len(pts))
#         smoothcoords= "smoothed: (" + str(sumposx) + "," + str(sumposy) + ")"
#         cv2.putText(frame, smoothcoords, (10,120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0))
        
        
        #drawing trail
        cv2.line(frame, pts[i-1],pts[i],(0,0,255), 1)
    
    #displaying video feed:
    cv2.imshow("Frame", frame)
    key= cv2.waitKey(5)# & 0xFF
    
    #to exit stream
    if key == 27: #esc key #ord("q"):
        print("esc key pressed")
        break
    
    framenumber=framenumber+1

#Stream end protocol:
print("VIDEO FEED STOPPED")

cv2.destroyAllWindows()
vs.stop()
