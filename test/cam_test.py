import picamera
import picamera.array
import time
import numpy as np
from PIL import Image
import cv2 as cv
import RPi.GPIO as GPIO

amp_mag = 20

def simple_threshold(im, threshold1, threshold2):
    img1 = ((im > threshold1) *100).astype("uint8")
    img2 = ((im > threshold2) *100).astype("uint8")
    ret = img1+img2
    return ret
    
def key2note(x, y):
    note_list=['do','re','mi','fa','so','la','xi']
    if y>300 or y<200:
        note = "Out"
    elif x<222 or x>390:
        note = "Out"
    else:
        idx=int((390-x)/24)
        note=note_list[idx]
    if note!="Out":
        print (note)

with picamera.PiCamera() as camera:
    camera.resolution = (640,480)
    camera.start_preview()
    time.sleep(3)
    camera.led = False
    while True:
        start_time = time.time()
        output = picamera.array.PiYUVArray(camera)
        camera.capture(output, 'yuv')
        gray_out=output.array[:,:,0]
        kernel = np.ones((5,5),np.uint8)
        opening = cv.morphologyEx(gray_out, cv.MORPH_OPEN, kernel)
        amp_out = opening*amp_mag
#        bin_img = simple_threshold(opening, 3, 4)
        ret,thresh = cv.threshold(opening,4,255,0)
        contours,hierarchy = cv.findContours(thresh, 1, 2)
        if len(contours)>0:
            for i,cnt in enumerate(contours):
                M = cv.moments(cnt)
                if M['m00']!=0:
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    key2note(cx,cy)
#                    print (i,":(",cx,",",cy,")")
#                rect = cv.minAreaRect(cnt)
#                box = cv.boxPoints(rect)
#                box = np.int0(box)
#                cv.drawContours(amp_out,[box],0,255,2)
        
        cv.imshow('cam',amp_out)
        if cv.waitKey(1) & 0xFF== ord('q'):
            break

camera.stop_preview()
# np.save("one_shot", gray_out)
# gray_out=np.load("one_shot.npy")
