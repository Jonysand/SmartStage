import picamera
import picamera.array
import time
import numpy as np
from PIL import Image
import cv2 as cv
import socket

# paramiters configure-----------------------------------------
amp_mag = 20
server_addr = '192.168.1.110'

def simple_threshold(im, threshold1, threshold2):
    img1 = ((im > threshold1) *100).astype("uint8")
    img2 = ((im > threshold2) *100).astype("uint8")
    ret = img1+img2
    return ret
    
def key2note(x, y):
    note_list=['do','re','mi','fa','so','la','xi']
    idx=int((50-x)/7.2)
#    note=note_list[idx]
    note = idx
    return note

#-------------------------------------------------------------------





# main program------------------------------------------------------

# connection to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((server_addr, 10000))
except:
    print("connect failed!")

old_note = [0,0,0,0,0,0,0]
# scanning fingers
with picamera.PiCamera() as camera:
    camera.resolution = (160,128)
    camera.start_preview()
    time.sleep(3)
    camera.led = False
    print ("start")
    while True:
        new_note = [0,0,0,0,0,0,0]
        output = picamera.array.PiYUVArray(camera)
        camera.capture(output, 'yuv')
        gray_out=output.array[:,:,0][50:70,60:110]
#        kernel = np.ones((5,5),np.uint8)
#        opening = cv.morphologyEx(gray_out, cv.MORPH_OPEN, kernel)
#        bin_img = simple_threshold(opening, 3, 4)
        ret,thresh = cv.threshold(gray_out,3,255,0)
        contours,hierarchy = cv.findContours(thresh, 1, 2)
        if len(contours)>0:
            for i,cnt in enumerate(contours):
                M = cv.moments(cnt)
                if M['m00']!=0:
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    note = key2note(cx,cy)
                    new_note[note]=1
        if old_note==new_note:
            continue
        else:
            data = ''.join(map(str,new_note))
            print (data)
            old_note = new_note
            s.send(data.encode())

camera.stop_preview()
