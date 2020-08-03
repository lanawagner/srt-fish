import cv2
import numpy as np
import os
import glob

#CAMERA CALIBRATION FOR RASPBERRY PI CAMERA v2

#setting criteria
CHECKERBOARD = (6,9) #6 x 9 inner corners
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

#array for object points
objpoints = []
imgpoints = []

objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2]=np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1,2)
prev_img_shape=None

#looping through calibration images
directory = ('/home/pi/Desktop/calibimages/')
for filename in os.listdir(directory): #return filename + size
    
    #read image
    pathname= os.path.join(directory, filename)
    img=cv2.imread(pathname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #print(pathname)
    
    #finding corners
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
    #print(pathname, ret)
    
    #refining and drawing corners
    if ret == True:
        objpoints.append(objp)
        
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1, -1), criteria)
        imgpoints.append(corners2)
        
        img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
        #cv2.imshow(pathname, img)
        #cv2.waitKey(0)
    elif ret == False:
        print(pathname, "Checkerboard not found")

#cv2.destroyAllWindows()
#h,w = img.shape[:2]


#saving the calibration matrix to a .yml file
ret, mtx, dist,rvecs,tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
cv_file = cv2.FileStorage('/home/pi/Desktop/srt-fish/picalibmatrix.yml', cv2.FILE_STORAGE_WRITE)
cv_file.write("K", mtx)
cv_file.write("D", dist)
cv_file.release()