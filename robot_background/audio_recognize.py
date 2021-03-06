# # -*- coding:utf-8 -*-
import websocket
from websocket import create_connection
import datetime
import hashlib
import base64
import hmac
import json
from hashlib import sha1
from urllib.parse import urlencode,quote
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import threading
import logging
import pyaudio
import wave
import socket
from multiprocessing import Process, Queue
# import _thread as thread

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

end_flag = 0

class AudioRecognizeWebsocket(Process):
    # 初始化
    def __init__(self, message_queue_input,audio_recognize_queue_output):
        super().__init__()
        self.APPID = '35dcd3b2'
        self.APIKey = 'f3a9201fdb7ba85e1a2d249168fc5c72'
        self.APISecret = 'YmE0MjExMmJhY2IxMjE3MTIzMmI4NDVk'
        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo":1,"vad_eos":10000}

        self.message_queue_input = message_queue_input #命令输入
        self.audio_recognize_queue_output = audio_recognize_queue_output #识别结果输出
        # print("收到的识别队列", self.audio_recognize_queue_output)
        self.data_change_lock = threading.Lock()  #线程锁
        self.data_store_buff = []
        self.max_store_size = 50

        self.process_end = False
        self.process_error = False
        self.ws = create_connection(self.create_url()) #创建链接,这里时候一个阻塞链接，如果没网就会卡在这里
    # 生成url,不用动，默认就行
    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url


    # 收到websocket消息的处理
    def on_message(self):
            while self.ws.connected:
                try:
                    message = str(self.ws.recv())
                    code = json.loads(message)["code"]
                    sid = json.loads(message)["sid"]
                    if code != 0:
                        errMsg = json.loads(message)["message"]
                        # print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
                        self.process_error = True

                    else:
                        data = json.loads(message)["data"]["result"]["ws"]
                        result = ""
                        for i in data:
                            for w in i["cw"]:
                                result += w["w"]
                        print(result)
                        self.audio_recognize_queue_output.put(result)
                except Exception as e:
                    print("receive msg,but parse exception:", e)

    def insert_data_tobuff(self, data): #输入bytes
        try:
            if (len(self.data_store_buff) + 1) > self.max_store_size:
                try:
                    self.data_change_lock.acquire()
                    del self.data_store_buff[0:10]
                finally:
                    self.data_change_lock.release()

            self.data_store_buff.append(data)
        except Exception as e:
            print("insert data error: ",e)

    def get_data(self):
        try:
            if self.data_store_buff :
                try:
                    self.data_change_lock.acquire()
                    data = self.data_store_buff.pop(0)
                except Exception:
                    print("获取数据错误")
                finally:
                    self.data_change_lock.release()
                return data
            else:
                return b''
        except Exception:
            print("获取数据错误")
            return b''
        
    def recv_voice_data(self): 
        # CHUNK = 5120#队列长度
        # FORMAT = pyaudio.paInt16 #保存格式
        # CHANNELS = 1  #几个通道
        # RATE = 8000 #采样率，一般8000的采样率能识别出人说的话
        # record_p = pyaudio.PyAudio() #实例化
        # #打开获取流
        # stream = record_p.open(format=FORMAT,
        #         channels=CHANNELS,
        #         rate=RATE,
        #         input=True,
        #         frames_per_buffer=CHUNK)

        while True:
            data, addr = self.receive_socket.recvfrom(5000)
            # print(len(data))
            self.insert_data_tobuff(data)
            # data = stream.read(640)
            # self.insert_data_tobuff(data)
        
        # stream.stop_stream()
        # stream.close()
        # record_p.terminate()

    # 收到websocket连接建立的处理
    def run(self):
        # frameSize = 1280  # 每一帧的音频大小
        intervel = 0.04  # 发送音频间隔(单位:s)
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧
        begin_time = datetime.now()
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) #允许重复绑定端口
        self.receive_socket.bind(("127.0.0.1", 8021))

        self.receive_recognize_result = threading.Thread(target=self.on_message) #接收识别结果
        self.receive_recognize_result.daemon = True #设为守护线程
        self.receive_recognize_result.start()

        self.receive_audio_thread = threading.Thread(target=self.recv_voice_data) #接收音频信号
        self.receive_audio_thread.daemon = True #守护线程
        self.receive_audio_thread.start()

        while True:
            if self.process_error:
                status = STATUS_LAST_FRAME
                self.audio_recognize_queue_output.put("timeout") #返回超时错误
            if (datetime.now() - begin_time).seconds > 60:
                status = STATUS_LAST_FRAME
                self.audio_recognize_queue_output.put("timeout") #返回超时错误
            try:
                input_cmd = self.message_queue_input.get(False)  #非阻塞，如果空就抛异常
                if input_cmd == "process_end":
                    status = STATUS_LAST_FRAME
            except:
                pass
            buf = self.get_data()
            # 文件结束
            if not buf and (status != STATUS_LAST_FRAME):
                print("没东西")
                time.sleep(0.5)
                continue
            # 第一帧处理
            # 发送第一帧音频，带business 参数
            # appid 必须带上，只需第一帧发送
            if status == STATUS_FIRST_FRAME:

                d = {"common": self.CommonArgs,
                    "business": self.BusinessArgs,
                    "data": {"status": 0, "format": "audio/L16;rate=8000",
                            "audio": str(base64.b64encode(buf), 'utf-8'),
                            "encoding": "raw"}}

                self.ws.send(json.dumps(d))
                status = STATUS_CONTINUE_FRAME
            # 中间帧处理
            elif status == STATUS_CONTINUE_FRAME:
                d = {"data": {"status": 1, "format": "audio/L16;rate=8000",
                            "audio": str(base64.b64encode(buf), 'utf-8'),
                            "encoding": "raw"}}
                self.ws.send(json.dumps(d))
            # 最后一帧处理
            elif status == STATUS_LAST_FRAME:
                d = {"data": {"status": 2, "format": "audio/L16;rate=8000",
                            "audio": str(base64.b64encode(b''), 'utf-8'),
                            "encoding": "raw"}}
                self.ws.send(json.dumps(d))
                time.sleep(1)
                # print("最后一帧")
                break
            # 模拟音频采样间隔
            time.sleep(intervel)
        self.ws.close()
        self.receive_socket.close()
        # print("关闭端口")


# if __name__ == "__main__":
#     # 测试时候在此处正确填写相关信息即可运行
#     time1 = datetime.now()
#     websocket.enableTrace(False)
#     message_queue = Queue()
#     audio_queue = Queue()
#     testprocess = AudioRecognizeWebsocket(message_queue,audio_queue)
#     testprocess.start()
#     while True:
#         if not testprocess.is_alive():
#             break
#         try:
#             w = audio_queue.get(False)
#             print("外面：",w)
#         except:
#             pass
#         time.sleep(0.1)
#     time2 = datetime.now()
#     print(time2-time1)
