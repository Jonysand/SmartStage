#coding=utf-8
import socket
import os
from scipy.io import wavfile
import pygame, pygame.sndarray
import numpy
import scipy.signal
import time
import threading
import re, urllib
from http.server import *
import subprocess
from bypy import ByPy

#-------recording config------------
global record_enable, record_flag, record_jud_flag, record_jud
record_enable = 1 # only when 1 can recording be activate
record_flag = 1 # 1 -> not recording, -1 -> recording
record_jud_flag = 0 # to flag if the timer start to judge whether to start/stop recording
global record, ten_sec_flag, start_time
record = numpy.zeros(shape = [441000,2], dtype = numpy.int16)
start_time = 0
ten_sec_flag = 1
global interval
#-----------------------------------

#---------------different mode of playing------------------
# left hand setting
left_offset = [] # only get multiple of 5, initially 0
for i in range(10):
    left_offset.append(0)

def left_key_play(mes):
    global record_enable, record_flag, record_jud_flag, record_jud, start_time, record, ten_sec_flag, left_offset, loop_tick
    glove = int(mes[1])
    hand = mes[2]
    note = mes[3:8]
    press_index = 0

    if hand == '1': # right hand
        if record_jud_flag == 1: #receive aother right hand mes, stop record judge
            record_jud.cancel()
            record_jud_flag = 0
        if note == "01000" and record_enable == 1: #start counting till 5s, then record start/stop
            record_jud_flag = 1
            record_jud = threading.Timer(5, record_start_stop)
            record_jud.daemon = True
            record_jud.start()
        for press in note:
            if press == '1':
                if (press_index+left_offset[glove])>=len(tone_list[tone_flag[glove]]):
                    continue
                if tone_list[tone_flag[glove]][press_index+left_offset[glove]][2] == 0:
                    tone_list[tone_flag[glove]][press_index+left_offset[glove]][1].play()
                elif tone_list[tone_flag[glove]][press_index+left_offset[glove]][2] == 1:
                    tone_list[tone_flag[glove]][press_index+left_offset[glove]][1].play(-1)
                elif tone_list[tone_flag[glove]][press_index+left_offset[glove]][2] != 1:
                    tone_list[tone_flag[glove]][press_index+left_offset[glove]][1].stop()
                if record_flag == -1 and tone_list[tone_flag[glove]][press_index+left_offset[glove]][2] == 0:
                    # recording this note
                    interval = time.time() - start_time
                    tick = int(interval*44100)
                    record[tick:(tick+len(tone_list[tone_flag[glove]][press_index+left_offset[glove]][0]))] += tone_list[tone_flag[glove]][press_index+left_offset[glove]][0]
                elif record_flag == -1 and tone_list[tone_flag[glove]][press_index+left_offset[glove]][2] == 1:
                    # set loop_flag to tick
                    interval = time.time() - start_time
                    tick = int(interval*44100)
                    tone_list[tone_flag[glove]][press_index+left_offset[glove]][2] = tick
                elif record_flag == -1 and tone_list[tone_flag[glove]][press_index+left_offset[glove]][2] != 1:
                    # recording this loop
                    interval = time.time() - start_time
                    tick = int(interval*44100)
                    loop_rec_len = tick - tone_list[tone_flag[glove]][press_index+left_offset[glove]][2]
                    times = int(loop_rec_len/len(tone_list[tone_flag[glove]][press_index+left_offset[glove]][0]))
                    for i in range(times):
                        record[(tone_list[tone_flag[glove]][press_index+left_offset[glove]][2]+i*len(tone_list[tone_flag[glove]][press_index+left_offset[glove]][0])):((tone_list[tone_flag[glove]][press_index+left_offset[glove]][2]+i*len(tone_list[tone_flag[glove]][press_index+left_offset[glove]][0]))+len(tone_list[tone_flag[glove]][press_index+left_offset[glove]][0]))] += tone_list[tone_flag[glove]][press_index+left_offset[glove]][0]
                    tone_list[tone_flag[glove]][press_index+left_offset[glove]][2] = 1
                elif record_flag == 1:
                    tone_list[tone_flag[glove]][press_index+left_offset[glove]][2]*=(-1)
            press_index+=1
                
    elif hand == '0': # left hand
        for press in note:
            if press == '1':
                left_offset[glove] = (4-press_index)*5
            press_index+=1


def ten_finger(mes):
    global record_enable, record_flag, record_jud_flag, record_jud, start_time, record, ten_sec_flag
    glove = int(mes[1])
    hand = mes[2]
    note = mes[3:8]
    press_index = 0

    if hand == '1': # right hand
        if record_jud_flag == 1: #receive aother right hand mes, stop record judge
            record_jud.cancel()
            record_jud_flag = 0
        if note == "01000" and record_enable == 1: #start counting till 5s, then record start/stop
            record_jud_flag = 1
            record_jud = threading.Timer(5, record_start_stop)
            record_jud.daemon = True
            record_jud.start()
        for press in note:
            if press == '1':
                if tone_list[tone_flag[glove]][press_index+5][2] == 0:
                    tone_list[tone_flag[glove]][press_index+5][1].play()
                elif tone_list[tone_flag[glove]][press_index+5][2] == 1:
                    tone_list[tone_flag[glove]][press_index+5][1].play(-1)
                elif tone_list[tone_flag[glove]][press_index+5][2] == -1:
                    tone_list[tone_flag[glove]][press_index+5][1].stop()
                tone_list[tone_flag[glove]][press_index+5][2]*=(-1)
                if record_flag == -1 and tone_list[tone_flag[glove]][press_index+5][2] != 1:
                    # recording this note
                    interval = time.time() - start_time
                    tick = int(interval*44100)
                    record[tick:(tick+len(tone_list[tone_flag[glove]][press_index+5][0]))] += tone_list[tone_flag[glove]][press_index+5][0]
            press_index+=1
                
    elif hand == '0': # left hand
         for press in note:
            if press == '1':
                if tone_list[tone_flag[glove]][press_index][2] == 0:
                    tone_list[tone_flag[glove]][press_index][1].play()
                elif tone_list[tone_flag[glove]][press_index][2] == 1:
                    tone_list[tone_flag[glove]][press_index][1].play(-1)
                elif tone_list[tone_flag[glove]][press_index][2] == -1:
                    tone_list[tone_flag[glove]][press_index][1].stop()
                tone_list[tone_flag[glove]][press_index][2]*=(-1)
                if record_flag == -1 and tone_list[tone_flag[glove]][press_index][2] != 1:
                    # recording this note
                    interval = time.time() - start_time
                    tick = int(interval*44100)
                    record[tick:(tick+len(tone_list[tone_flag[glove]][press_index][0]))] += tone_list[tone_flag[glove]][press_index][0]
            press_index+=1
        
#----------------------------------------------------------

def add_new_sound(List, dir_path, mode):
    # List: tone_list
    # dir_path: target tone folder
    # mode: function used to play music
    note_list = []
    cue_file = open(dir_path+"/"+"cue.txt")
    filenames = cue_file.readlines()
    for filename in open(dir_path+"/"+"cue.txt"):
        filename = filename.strip('\n')
        if "loop" in filename:
            loop_flag = 1
        else:
            loop_flag = 0
        fs, array = wavfile.read(dir_path+"/"+filename+".wav")
        sound = pygame.sndarray.make_sound(array)
        note_list.append([array,sound,loop_flag])
    note_list.append(mode)
    List.append(note_list)
    return List
        

def test_ping():
    global ping_test_flag, IP_list, record_flag
    ping_test_flag = 0
    while True:
        if ping_test_flag == 0:
            for gloves in IP_list:
                proc = subprocess.Popen(['ping', gloves[1]],stdout=subprocess.PIPE)
                time.sleep(2)
                proc.kill()
                result = proc.stdout.read().decode()
                if '64 bytes' not in result:
                    noti_disconnected.play(0)
                    print (gloves[1]," disconnected") # send notification to WeApp
                    IP_list.remove(gloves)
                    if IP_list == []:
                        record_flag = 1
        else:
            break

def release_port():
    ret = os.popen("lsof -i:10000")
    all_list = ret.read()
    line_list = all_list.split('\n')
    for i in range(len(line_list)-2):
        each_list = line_list[i+1].split(' ')
        process_num = each_list[2]
        command_line = "kill -9 "+process_num
        os.system(command_line)

def record_start_stop():
    global record_enable, record_flag, record_jud_flag, record_jud, record, start_time, tone_list, tone_flag, ten_sec_flag
    record_jud_flag = 0
    record_flag = (-1) * record_flag
    if record_flag == -1:
        print ("record start!")
        noti_rec_start.play(0)
        record = numpy.zeros(shape = [441000,2], dtype = numpy.int16)
        ten_sec_flag = 1 # to extend reacord with 0
        start_time = time.time()
        record_jud.cancel()
    elif record_flag == 1:
        noti_rec_stop.play(0)
        print ("saving...")
        zero_num = 0
        i = 1
        while True:
            if (record[len(record)-i] == record[0]).any():
                zero_num+=1
                i+=1
            else:
                break
        record = record[:len(record)-1-zero_num]

        now = time.time()
        now_time = time.strftime("%Y%m%d_%H%M%S")
        path = (now_time+".wav")
        wavfile.write(path, 44100, record)
        print ("local saved!")

        proc = subprocess.Popen(['ping','www.baidu.com'],stdout=subprocess.PIPE)
        time.sleep(2)
        proc.kill()
        result = proc.stdout.read().decode()
        if '64 bytes' in result:
            bp = ByPy()
            bp.mkdir(remotepath='music')
            bp.upload(localpath=path, remotepath='music',ondup='newcopy')
            print ("uploaded!")
        else:
            print ("network disconnected!")

    record_jud.cancel()
    record = numpy.zeros(shape = [441000,2], dtype = numpy.int16)
    
def acpt_proc():
    while True:
        new_sock, new_addr = server.accept()
        t = threading.Thread(target=receive_data,args=(new_sock, new_addr), name=str(new_addr[0]))
        t.start()

def receive_data(sock, addr):
    global record_enable, record_flag, record_jud_flag, record_jud, start_time, record, ten_sec_flag, IP_list
    while True:
        data = sock.recv(1024)
##        if not data:
##            print ("dis!")
##            for gloves in IP_list:
##                if gloves[1]==addr:
##                    print (gloves[1]," disconnected") # send notification to WeApp
##                    IP_list.remove(gloves)
##                    noti_disconnected.play(0)
##                    break
        mes_type = data.decode()[0]
        #------mes of getting IP from gloves-----
        if mes_type == '0':
            noti_connected.play(0)
            print ("new glove connected!")
            glove = data.decode()[1]
            ip = addr[0]
            IP_list.append([glove, ip])
        #--------------------------------
        #------mes of playing------------
        if mes_type == '1':
            tone_list[tone_flag[int(data.decode()[1])]][-1](data.decode())
        #------------------------------
        #print (addr)
        #print (data.decode())

#--------server information---------
# get local device name
myname = socket.getfqdn(socket.gethostname())
# get this ip address
myaddr = socket.gethostbyname(myname)
print ("NAME: ",myname)
print ("IP: ",myaddr)
print ("")
#------------------------------------

#--------server main-----------------
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
release_port()

server.bind(('192.168.1.101', 10000))
server.listen(6)

    #--------load wav file--------------
global tone_list, tone_flag
# Structure of tone_list:
# tone_list consists of note_lists
# note_list consists of [array,sound,loop_flag] [array,sound,loop_flag] ... mode
tone_list = [] #to store different tones, use tone_flag to rep different tones
tone_flag = [] # 0:guitar_chor, 1:piano_chor, 2:piano_note
for i in range(10):
    tone_flag.append(4)
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

tone_list = add_new_sound(tone_list, "guitar_chor", left_key_play)
tone_list = add_new_sound(tone_list, "piano_chor", left_key_play)
tone_list = add_new_sound(tone_list, "piano_note", left_key_play)
tone_list = add_new_sound(tone_list, "penta", left_key_play)
tone_list = add_new_sound(tone_list, "star", ten_finger)
tone_list = add_new_sound(tone_list, "Mission_Impossible", left_key_play)
tone_list = add_new_sound(tone_list, "Childhood", ten_finger)
    #-----------------------------------


    #----------http server--------------
global set_glove
set_glove = 0
class httpServer(BaseHTTPRequestHandler):
    #小程序端使用的http方法为GET方法 这里就是处理过来的GET请求
    def do_GET(self):
        global set_glove, record_enable, IP_list, tone_flag
        templateStr='Failed!'
        #这里的self.path就是小程序端发来的数据 是一个字符串类型
        getData=self.path
        print ('URL=',getData)
        #下面是对收到的请求进行解析 我觉得可以在每个if下添加脚本调用的操作
        if(re.search('Solo',getData)!=None):
            templateStr='Mode:Solo!'
            record_enable = 1
        if(re.search('Duet',getData)!=None):
            templateStr='Mode:Duet!'
            record_enable = 0
        if (re.search('guitar_chor', getData) != None):
            templateStr = 'Instr:Guitar Chor!'
            tone_flag[set_glove] = 0
        if (re.search('piano_chor', getData) != None):
            templateStr = 'Instr:Piano Chor!'
            tone_flag[set_glove] = 1
        if (re.search('piano_note', getData) != None):
            templateStr = 'Instr:Piano Note!'
            tone_flag[set_glove] = 2
        if (re.search('penta', getData) != None):
            templateStr = 'Instr:Penta!'
            tone_flag[set_glove] = 3
        if (re.search('twinkle_star', getData) != None):
            templateStr = 'Instr:Twinkle Star'
            tone_flag[set_glove] = 4
        if (re.search('mission_impossible', getData) != None):
            templateStr = 'Instr:Mission Impossible!'
            tone_flag[set_glove] = 5
        if (re.search('childhood', getData) != None):
            templateStr = 'Instr:Childhood!'
            tone_flag[set_glove] = 6
        if (re.search('0', getData) != None):
            templateStr = 'Now:Glove0!'
            set_glove = 0
        if (re.search('1', getData) != None):
            templateStr = 'Now:Glove1!'
            set_glove = 1
        if (re.search('2', getData) != None):
            templateStr = 'Now:Glove2!'
            set_glove = 2
        if (re.search('glove_nums', getData) != None):
            S = ""
            glove_id = []
            for gloves in IP_list:
                if gloves[0] not in glove_id:
                    S = (S+"手套"+str(gloves[0])+",")
                    glove_id.append(gloves[0])
            templateStr = S[:-1]
        #下面是设置返回给小程序的报文格式和内容
        self.protocol_version='HTTP/1.1'
        self.send_response(200)
        self.send_header("Welcome","Contect")
        self.end_headers()
        templateStr = bytes(templateStr.encode())
        self.wfile.write(templateStr)

#这个就是开启http服务的函数
def start_server(port):
    http_server=HTTPServer(('',int(port)),httpServer)
    http_server.serve_forever()

#使用2500端口 开启服务
Http_receiver = threading.Thread(target=start_server, args=(2500,), name = "HTTP_server")
Http_receiver.start()
    #------------------------------------

print("Start!")
noti_sys_start.play(0)

global IP_list
IP_list = [] # to save IP addrs from gloves

ping_threat = threading.Thread(target = test_ping, name="Ping_Test")
ping_threat.start()
# log: replaced by method of sock.receive

acpt = threading.Thread(target=acpt_proc, name = "ACCEPTING")
acpt.start()

zero_list = numpy.zeros(shape = [220500,2], dtype = numpy.int16)
ten_sec_flag = 1
try:
    while True:
        # if recording, following code used to extend record array
        if record_flag == -1:
            interval = time.time() - start_time
            if interval >= (5*ten_sec_flag):
                record = numpy.vstack((record,zero_list))
                ten_sec_flag+=1;
        
finally:
    print ("server closing")
##    ping_test_flag = 1
##    ping_threat.join(timeout=0)
    server.close()
#------------------------------------

