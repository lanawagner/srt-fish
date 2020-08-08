import cv2
import numpy as np
import os
import glob

#load matrix
# cv_file = cv2.FileStorage('/home/pi/Desktop/srt-fish/picalibmatrix.yml', cv2.FILE_STORAGE_READ)
# camera_matrix = cv_file.getNode("K").mat()
# dist_matrix = cv_file.getNode("D").mat()
#THESE ARE NOT THE CORRECT VALUES! FIX LATER!
camera_matrix = [ 1.5023540204125525e+03, 0., 9.6062940467428859e+02, 0.,1.5104529904534113e+03, 5.7615923977773048e+02, 0., 0., 1. ]
camera_matrix = np.reshape(camera_matrix,(3,3))
dist_matrix = [ 6.4520603663317397e-02, 1.5396120777939031e+00,6.4735652511072658e-03, -3.9846974746375190e-04,-8.9381338909684924e+00 ]
dist_matrix = np.reshape(dist_matrix,(1,5))

print("K", camera_matrix)
print("D", dist_matrix)

#UNDISTORTING, FIGURE OUT WHY UNDISTORTED IMAGE HAS NO DATA
img=cv2.imread('/home/pi/Desktop/calibimages/test7.jpg')
h,w = img.shape[:2]

newcameramtx, roi=cv2.getOptimalNewCameraMatrix(camera_matrix,dist_matrix,(w,h),1,(w,h))

dst = cv2.undistort(img,camera_matrix,dist_matrix,None,camera_matrix)

cv2.imshow("undistorted", dst)
cv2.waitKey(0)

# x,y,w,h = roi
# dst = dst[y:y+h, x:x+w]
# cv2.imwrite('/home/pi/Desktop/calibtestresult.jpg',dst)
# 
# result = cv2.imread('/home/pi/Desktop/calibtestresult.jpg')
# cv2.imshow("undistorted", result)
# cv2.waitKey(0)