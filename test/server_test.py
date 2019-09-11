#coding=utf-8
import socket
import os
from scipy.io import wavfile
import pygame, pygame.sndarray
import numpy as np
import scipy.signal
import time
import threading
import subprocess
import keyboard
import cv2 as cv
import json

# funtions.parameters definition-----------------------------------------------
global tone_flag, rec_flag, record, interval, start_time, tone_name_list, ten_sec_flag, old_tone
tone_flag = 0 #instrument index
rec_flag = 1 #state of recording
record = np.zeros(shape = [441000,2], dtype = np.int16)
ten_sec_flag = 1
tone_name_list = []
old_tone = 0


def release_port():
    ret = os.popen("lsof -i:10000")
    all_list = ret.read()
    line_list = all_list.split('\n')
    for i in range(len(line_list)-2):
        each_list = line_list[i+1].split(' ')
        process_num = each_list[2]
        command_line = "kill -9 "+process_num
        os.system(command_line)


def key2note(x, y):
    note_list=['do','re','mi','fa','so','la','xi']
    idx=int((50-x)/7.2)
    #    note=note_list[idx]
    note = idx
    return note


def findFinger(gray_out):
    new_note = [0,0,0,0,0,0,0]
    ret,thresh = cv.threshold(gray_out,3,255,cv.THRESH_BINARY)
    binary, contours, hierarchy = cv.findContours(thresh, 1, 2)
    if len(contours)>0:
        for i,cnt in enumerate(contours):
            M = cv.moments(cnt)
            if M['m00']!=0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                note = key2note(cx,cy)
                new_note[note]=1
    return new_note


def receive_data(sock, addr):
    global tone_flag, rec_flag, record, interval, start_time, tone_name_list, ten_sec_flag
    old_note = [0,0,0,0,0,0,0]
    data_size = 3040
    while True:
        data = sock.recv(1024)
        if not data:
            break
        received_size  = len(data)
        received_data = data
        while received_size<data_size:
            data = sock.recv(1024)
            received_size += len(data)
            received_data += data
        out_list = json.loads(received_data.decode())
        gray_out = np.array(out_list)
        gray_out = gray_out.astype(np.uint8)
        new_note = findFinger(gray_out)
        if old_note==new_note:
            continue
        else:
            old_note = new_note
        print (new_note)
        for idx, press in enumerate(new_note):
            if press == 1:
                tone_list[tone_flag][idx][1].play()
                if rec_flag == -1:
                    interval = time.time() - start_time
                    tick = int(interval*44100)
                    record[tick:(tick+len(tone_list[tone_flag][idx][0]))]+=tone_list[tone_flag][idx][0]




def add_new_sound(List, dir_path):
    # List: tone_list
    # dir_path: target tone folder
    tone_name_list.append(dir_path)
    note_list = []
    cue_file = open(dir_path+"/"+"cue.txt")
    filenames = cue_file.readlines()
    for filename in open(dir_path+"/"+"cue.txt"):
        filename = filename.strip('\n')
        fs, array = wavfile.read(dir_path+"/"+filename+".wav")
        sound = pygame.sndarray.make_sound(array)
        note_list.append([array,sound])
    List.append(note_list)
    return List


def acpt_proc():
    while True:
        new_sock, new_addr = server.accept()
        t = threading.Thread(target=receive_data,args=(new_sock, new_addr), name=str(new_addr[0]))
        t.start()


def listen_key():
    global tone_flag, rec_flag, record, interval, start_time, tone_name_list, ten_sec_flag, old_tone
    while True:
        key = keyboard.read_event()
        if key.event_type=='up':
            key = key.name
            # change the instrument
            if key>='0' and key<='9':
                new_tone = int(key)-1
                if new_tone == old_tone or (new_tone+1)>=len(tone_name_list):
                    continue
                else:
                    tone_flag = new_tone
                    old_tone = new_tone
                print ("Instrument Changed to:",tone_name_list[tone_flag])

            # start/stop recording
            elif key=='r':
                if rec_flag == 1:
                    record = np.zeros(shape = [441000,2], dtype = np.int16)
                    print ("record start!")
                    noti_rec_start.play(0)
                    start_time = time.time()
                    rec_flag=rec_flag*(-1)
                elif rec_flag == -1:
                    noti_rec_stop.play(0)
                    print ("saving...")
                    zero_num = 0
                    i = 1
                    try:
                        while True:
                            if (record[len(record)-i] == record[0]).any():
                                zero_num+=1
                                i+=1
                            else:
                                break
                        record = record[:len(record)-1-zero_num]
                    except:
                        print ("Empty record!")
                        continue
                    now = time.time()
                    now_time = time.strftime("%Y%m%d_%H%M%S")
                    path = (now_time+".wav")
                    wavfile.write(path, 44100, record)
                    print ("local saved!")
                    rec_flag=rec_flag*(-1)
            else:
                continue


def recording_proc():
    global tone_flag, rec_flag, record, interval, start_time, tone_name_list, ten_sec_flag
    try:
        while True:
            if rec_flag == -1:
                interval = time.time() - start_time
                if interval >= (5*ten_sec_flag):
                    record = np.vstack((record,zero_list))
                    ten_sec_flag+=1;
    finally:
        print ("server closing")










# server info----------------------------------------------------------
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
release_port()

server.bind(('192.168.1.110', 10000))
server.listen(4)








# loading sound--------------------------------------------------------
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
fs, noti_connected_array = wavfile.read("connected.wav")
noti_connected = pygame.sndarray.make_sound(noti_connected_array)
fs, noti_disconnected_array = wavfile.read("disconnected.wav")
noti_disconnected = pygame.sndarray.make_sound(noti_disconnected_array)
fs, rec_start_array = wavfile.read("record_start.wav")
noti_rec_start = pygame.sndarray.make_sound(rec_start_array)
fs, rec_stop_array = wavfile.read("record_stop.wav")
noti_rec_stop = pygame.sndarray.make_sound(rec_stop_array)
fs, sys_start_array = wavfile.read("sys_start.wav")
noti_sys_start = pygame.sndarray.make_sound(sys_start_array)
tone_list = []
tone_list = add_new_sound(tone_list, "piano_note")








# main---------------------------------------------------------------------
print("Start!")
noti_sys_start.play(0)

# start connecting
acpt = threading.Thread(target=acpt_proc, name = "ACCEPTING")
acpt.start()

# start recording process
zero_list = np.zeros(shape = [220500,2], dtype = np.int16)
rec_proc = threading.Thread(target=recording_proc, name = "RECORDING")
rec_proc.start()

print ("Press number to change the instrument, press R to start/stop recording")
print (''.join(tone_name_list))
listen_key()
