from picamera.array import PiRGBArray
from picamera import PiCamera
from imutils.video import VideoStream
from imutils.video import FPS
import time
import imutils
import cv2
import numpy as np

#CAMERA CALIBRATION FOR RASPBERRY PI CAMERA v2 FROM VIDEO FEED

#camera video setup
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
fps = FPS().start()
print("STARTING VIDEO FEED")

#OLD:
# camera = PiCamera()
# camera.resolution = (640, 480)
# camera.framerate=32
# rawCapture = PiRGBArray(camera, size=(640,480))

#setting criteria
CHECKERBOARD = (6,9) #6 x 9 inner corners
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

#array for object points
objpoints = []
imgpoints = []

objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2]=np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1,2)
prev_img_shape=None

#VIDEO FEED, LOOPING THROUGH IMAGE FRAMES
#for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
while True:
    #img = frame.array
    frame = vs.read()
    
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    
    #print(gray.shape)

#     #finding corners
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
    
    #print(pathname, ret)
#     
#     #refining and drawing corners
    if ret == True:
        print("c found")
        objpoints.append(objp)
        
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1, -1), criteria)
        imgpoints.append(corners2)
#         
        #frame = cv2.drawChessboardCorners(frame , CHECKERBOARD, corners2, ret)
    
    #cv2.imshow("Frame", img)
    cv2.imshow("Frame", frame)
    key= cv2.waitKey(5)# & 0xFF
    
    if key == 27: #esc key #ord("q"):
        print("esc key pressed")
        break
    
    fps.update()

#saving the calibration matrix to a .yml file
#print("OP", objpoints)
#print("IP",imgpoints)
ret, mtx, dist,rvecs,tvecs = cv2.calibrateCamera(objpoints, imgpoints, (320,240), None, None)
print("K", mtx)
print("D", dist)


# print("writing to file")
# cv_file = cv2.FileStorage('/home/pi/Desktop/srt-fish/picalibvideomatrix.yml', cv2.FILE_STORAGE_WRITE)
# cv_file.write("K", mtx)
# cv_file.write("D", dist)
# cv_file.release()

#K: [[177.03120335   0.         166.73836584][  0.         176.26172836 126.89791006][  0.           0.           1.        ]]
#D: [[ 0.51413493 -1.50449121 -0.00173984  0.02121675  1.35833619]]

#h,w = img.shape[:2]


print("VIDEO FEED STOPPED")

cv2.destroyAllWindows()
vs.stop()

# cv2.destroyAllWindows()
# vs.stop()
