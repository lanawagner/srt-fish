import cv2
import numpy as np
import os
import glob

CHECKERBOARD = (6,9)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objpoints = []
imgpoints = []

objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2]=np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1,2)
prev_img_shape=None

directory = ('/home/pi/Desktop/calibimages/')
for filename in os.listdir(directory): #return filename + size
    
    #read image
    pathname= os.path.join(directory, filename)
    img=cv2.imread(pathname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
 #   print(pathname)
    
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
#     print(pathname, ret)    
    if ret == True:
        objpoints.append(objp)
        
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1, -1), criteria)
        imgpoints.append(corners2)
        
        img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
        #cv2.imshow(pathname, img)
        #cv2.waitKey(0)
    elif ret == False:
        print(pathname, "something's wrong")

#cv2.destroyAllWindows()
#h,w = img.shape[:2]

ret, mtx, dist,rvecs,tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
# print("Camera matrix: \n")
# print(mtx)
# print("dist : \n")
# print(dist)
# print("rvecs : \n")
# print(rvecs)
# print("tvecs : \n")
# print(tvecs)

img=cv2.imread('test7.jpg')
#h,w = testim.shape[:2]

h,w = img.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

mapx,mapy=cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w,h),5)
dst = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)

x,y,w,h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite('calibtestresult.png',dst)