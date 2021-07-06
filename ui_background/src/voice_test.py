import pyaudio
import wave
import sys
import socket
import threading
import requests
import struct
import time

end_flag = False

def end_th():
    global end_flag
    while True:
        na = input("按q停止：")
        print(na)
        if na == 'q':   
            end_flag = True
            break

#语音用udp传输，虽然会丢失信息，但是速度快，tcp用来传输重要信息，单开一个socket链接
def record_audio():
    global end_flag
    response = requests.get("http://101.37.16.240:62222/gs-robot/cmd/open_speak",timeout=3)
    print(response.status_code)
    print(response.content)
    CHUNK = 1280#队列长度
    FORMAT = pyaudio.paInt16 #保存格式
    CHANNELS = 1  #几个通道
    RATE = 8000 #采样率，一般8000的采样率能识别出人说的话
    record_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip_port = ('101.37.16.240', 62222)
    record_socket.connect(ip_port)#尝试链接服务器
    content = b"client_speak \r\n"
    record_socket.sendall(content)#注册身份
    time.sleep(2)
    record_p = pyaudio.PyAudio() #实例化
    #打开获取流
    stream = record_p.open(format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK)
    
    #获取音频信息并发送
    while(True):
        if end_flag:
            break
        data = stream.read(640)
        fhead = struct.pack('II',12,len(data))
        try:
            record_socket.send(fhead) 
            record_socket.send(data)
        except Exception:
            pass

    stream.stop_stream()
    stream.close()
    record_p.terminate()
    record_socket.close()
    response = requests.get(f"http://101.37.16.240:62222/gs-robot/cmd/close_speak",timeout=3)
    print(response.content)
#udp

def run():
    record_audio_thread = threading.Thread(target=record_audio)  #创建socket链接线程
    record_audio_thread.start()
    end_thread = threading.Thread(target=end_th)  #创建socket链接线程
    end_thread.start()


if __name__ == '__main__':
    run()



    # wf = wave.open(wave_out_path, 'wb')
    # wf.setnchannels(CHANNELS)
    # wf.setsampwidth(p.get_sample_size(FORMAT))
    # wf.setframerate(RATE)
    # stream = p.open(format=FORMAT,
    #     channels=CHANNELS,
    #     rate=RATE,
    #     output=True,
    #     frames_per_buffer=CHUNK)
    
    # wf = wave.open(wave_out_path, 'rb')
    # data = wf.readframes(CHUNK)
    # while len(data) > 0:
            #stream.write(data)
        # data = wf.readframes(CHUNK)
    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #sock.connect(ip_port)