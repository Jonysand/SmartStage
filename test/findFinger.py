"""
img size: 640*480
"""

import time
import numpy as np
from PIL import Image
import cv2 as cv

def simple_threshold(im, threshold1, threshold2):
    img1 = ((im > threshold1) *100).astype("uint8")
    img2 = ((im > threshold2) *100).astype("uint8")
    ret = img1+img2
    return ret

gray_out=np.load("one_shot.npy")

amp_mag = 20


kernel = np.array([
[1,2,1],
[2,4,2],
[1,2,1]
])
kernel = kernel/kernel.sum()

kernel = np.ones((5,5),np.uint8)
opening = cv.morphologyEx(gray_out, cv.MORPH_OPEN, kernel)

amp_out = opening*amp_mag
img = Image.fromarray(amp_out)
img.show()

ret,thresh = cv.threshold(opening,2,255,0)
contours,hierarchy = cv.findContours(thresh, 1, 2)
cnt = contours[0]
M = cv.moments(cnt)
print( M )

#cv.imshow('conv', after_conv)
#cv.waitKey(1)

#index = np.unravel_index(gray_out.argmax(), gray_out.shape)
#print (index)
#print (gray_out[index])