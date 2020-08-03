import cv2
import numpy as np
import os
import glob

#load matrix
cv_file = cv2.FileStorage('/home/pi/Desktop/srt-fish/picalibmatrix.yml', cv2.FILE_STORAGE_READ)
camera_matrix = cv_file.getNode("K").mat()
dist_matrix = cv_file.getNode("D").mat()

print("K", camera_matrix)
print("D", dist_matrix)

#UNDISTORTING, FIGURE OUT WHY UNDISTORTED IMAGE HAS NO DATA
img=cv2.imread('/home/pi/Desktop/calibimages/test7.jpg')
h,w = img.shape[:2]

#h, w = gray.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(camera_matrix,dist_matrix,(w,h),1,(w,h))

dst = cv2.undistort(img,camera_matrix,dist_matrix,None,camera_matrix)

x,y,w,h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite('/home/pi/Desktop/calibtestresult.jpg',dst)

result = cv2.imread('/home/pi/Desktop/calibtestresult.jpg')
cv2.imshow("undistorted", result)
cv2.waitKey(0)