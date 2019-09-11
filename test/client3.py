import picamera
import picamera.array
import time
import numpy as np
import socket
import json

# paramiters configure-----------------------------------------
server_addr = '192.168.1.110'

# main program------------------------------------------------------

# connection to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((server_addr, 10000))
    s.send("connInstrument1")
except:
    print("connect failed!")

with picamera.PiCamera() as camera:
    camera.resolution = (160,128)
    camera.start_preview()
    time.sleep(3)
    camera.led = False
    print ("start")
    while True:
        output = picamera.array.PiYUVArray(camera)
        camera.capture(output, 'yuv')
        gray_out=output.array[:,:,0][50:70,60:110]
        out_list = gray_out.tolist()
        out_json = json.dumps(out_list)
        out_encode = out_json.encode()
        print (len(out_encode))
        s.send(out_encode)

camera.stop_preview()
