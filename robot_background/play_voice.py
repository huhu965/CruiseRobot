import sys
import os
import threading
import pyaudio
import wave
import time
from multiprocessing import Process
import datetime
import socket

# #当前文件路径
# print(os.path.realpath(__file__))
# #当前文件所在的目录，即父路径
# print(os.path.split(os.path.realpath(__file__))[0])

# #存放音源的绝对路径
# voice_source_path = os.path.split(os.path.realpath(__file__))[0]

voice_name_dict = {
    "开始初始化":"begin_init.wav",
    "链接服务器失败":"connect_server_fail.wav",
    "执行巡航任务":"execute_navigate_task.wav",
    "初始化完成":"init_finish.wav",
    "自我介绍":"introduce_myself.wav",
    "再回答一次":"respond_again.wav",
    "回答正确":"respond_correct.wav",
    "回答错误":"respond_error.wav",
    "考核开始":"start_exam.wav",
    "考核结束":"end_exam.wav",
    "考核通过":"pass_exam.wav",
    "考核没通过":"failed_exam.wav",
    "电池电量低":"warning_battery.wav",
    "初始化位置": "init_position.wav",
    "链接服务器失败": "connect_server_fail.wav",
    "响应唤醒": "respond_awake.wav",
}

class PlayVoice(Process):
    def __init__(self,name):
        super(PlayVoice, self).__init__()
        self.name = name
        self.voice_name_dict = voice_name_dict
        voice_source_path = "./voice_source"
        self.wf =  wave.open(voice_source_path + f"/{self.voice_name_dict[self.name]}", 'rb')
        self._is_playing = True
    def is_playing(self):
        return self._is_playing
    def run(self):
        #存放音源的绝对路径
        CHUNK = 1024#队列长度
        FORMAT = pyaudio.paInt16 #保存格式
        CHANNELS = 1  #几个通道
        RATE = 8000 #采样率，一般8000的采样率能识别出人说的话'
        self.record_p = pyaudio.PyAudio() #实例化 这里要放在run里，不然不在一个进程会报错 init的时候还在父进程
        #打开获取流
        self.stream = self.record_p.open(format=FORMAT,
                channels=CHANNELS,
                rate=self.wf.getframerate(),
                output=True,
                frames_per_buffer=CHUNK)
        
        data = self.wf.readframes(1024)
        while len(data)>0:
            self.stream.write(data)
            data = self.wf.readframes(1024)

        time.sleep(0.5)
        self.stream.stop_stream()
        self.stream.close()
        self.record_p.terminate()
        self._is_playing = False

class robot_awake_Process(Process):
    def __init__(self,ip_port):
        super(robot_awake_Process, self).__init__()
        self.ip_port = ip_port
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #接收音频信号

    def run(self):
        self.receive_socket.bind(self.ip_port)
        while True:
            data, addr = self.receive_socket.recvfrom(5000)
            if data.startswith(b'GET'):
                try:#分割url
                    request_head = data.decode("utf-8").split("\r\n")[0]
                    url = request_head.split(' ')[1]
                    space, name, modules, func = url.split("/")
                except Exception as e:
                    print(e)
                    continue
                if func == 'voice_awake':
                    p = PlayVoice("响应唤醒")
                    p.start()