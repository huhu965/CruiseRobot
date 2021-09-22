import sys
import os
import threading
import pyaudio
import wave
import time
import json
from multiprocessing import Process
import datetime
import socket

# #当前文件路径
# print(os.path.realpath(__file__))
# #当前文件所在的目录，即父路径
# print(os.path.split(os.path.realpath(__file__))[0])

# #存放音源的绝对路径
# voice_source_path = os.path.split(os.path.realpath(__file__))[0]

class PlayVoice(Process):
    def __init__(self,file_path):
        super(PlayVoice, self).__init__()
        # with open("question_param.json","r") as file: #读入题目
        #     self.voice_name_dict = json.load(file)
        # voice_source_path = "./voice_source"
        self.wf =  wave.open(file_path, 'rb')
        self._is_playing = True
        print("初始化")

    def is_playing(self):
        return self._is_playing
        
    def run(self):
        try:
            print("*********第一步")
            #存放音源的绝对路径
            CHUNK = 1024#队列长度
            FORMAT = pyaudio.paInt16 #保存格式
            CHANNELS = 1  #几个通道
            RATE = 8000 #采样率，一般8000的采样率能识别出人说的话'
            self.record_p = pyaudio.PyAudio() #实例化 这里要放在run里，不然不在一个进程会报错 init的时候还在父进程
            #打开输出流
            self.stream = self.record_p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=self.wf.getframerate(),
                    output=True,
                    frames_per_buffer=CHUNK)
            print("*********第二步")
            data = self.wf.readframes(1024)
            while len(data)>0:
                self.stream.write(data)
                data = self.wf.readframes(1024)
            print("*********第三步")
            time.sleep(0.5)
            self.stream.stop_stream()
            self.stream.close()
            self.record_p.terminate()
            self._is_playing = False
            print("*********第四步")
        except Exception as e:
            print("PlayVoice run:",e)

def play_system_audio(name):
    with open("question_param.json","r") as file: #读入题目
        voice_name_dict = json.load(file)
    voice_source_path = "./voice_source/"
    system_play_handle = PlayVoice(voice_source_path + voice_name_dict["SystemVoice"][name])
    print("****************播放开始：",datetime.datetime.now())
    system_play_handle.start()
    system_play_handle.join()#等待音频播放完
    print("****************播放结束：",datetime.datetime.now())
    system_play_handle = None
