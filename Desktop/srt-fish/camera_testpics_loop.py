from picamera import PiCamera
from time import sleep
import os

camera = PiCamera()
# i=10

for i in range (0,14):
    camera.start_preview()
    sleep(3)
    #camera.capture('/home/pi/Desktop/test_9.jpg')
    camera.capture('/home/pi/Desktop/calibimages/a.jpg')
    camera.stop_preview()
    dst = "test" + str(i) + ".jpg"
    src = '/home/pi/Desktop/calibimages/a.jpg'
    dst = '/home/pi/Desktop/calibimages/' + dst
    os.rename(src, dst)
    sleep(3)
