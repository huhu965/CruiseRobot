# -*- coding:utf-8 -*-
#
#   author: iflytek
#  本demo测试成功运行时所安装的第三方库及其版本如下，您可自行逐一或者复制到一个新的txt文件利用pip一次性安装：
#   cffi==1.12.3
#   gevent==1.4.0
#   greenlet==0.4.15
#   pycparser==2.19
#   six==1.12.0
#   websocket==0.2.1
#   websocket-client==0.56.0
#
#  语音听写流式 WebAPI 接口调用示例 接口文档（必看）：https://doc.xfyun.cn/rest_api/语音听写（流式版）.html
#  webapi 听写服务参考帖子（必看）：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=38947&extra=
#  语音听写流式WebAPI 服务，热词使用方式：登陆开放平台https://www.xfyun.cn/后，找到控制台--我的应用---语音听写（流式）---服务管理--个性化热词，
#  设置热词
#  注意：热词只能在识别的时候会增加热词的识别权重，需要注意的是增加相应词条的识别率，但并不是绝对的，具体效果以您测试为准。
#  语音听写流式WebAPI 服务，方言试用方法：登陆开放平台https://www.xfyun.cn/后，找到控制台--我的应用---语音听写（流式）---服务管理--识别语种列表
#  可添加语种或方言，添加后会显示该方言的参数值
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import threading
import pyaudio
import wave
import socket
# import _thread as thread

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

end_flag = 0
receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receive_socket.bind(("127.0.0.1", 8001))
voice_data_buf = bytes()
max_size = 64000

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, AudioFile):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo":1,"vad_eos":10000}

    # 生成url
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
def on_message(ws, message):
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))

        else:
            data = json.loads(message)["data"]["result"]["ws"]
            # print(json.loads(message))
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            print("sid:%s call success!,data is:%s" % (sid, json.dumps(data, ensure_ascii=False)))
    except Exception as e:
        print("receive msg,but parse exception:", e)

def insert_data_tobuff(data):
    global voice_data_buf
    length_data = len(data)
    if (len(voice_data_buf) + length_data) > max_size:
        voice_data_buf = voice_data_buf[length_data:] + data
    else:
        voice_data_buf = voice_data_buf + data

def get_data(data_size):
    global voice_data_buf
    if(len(voice_data_buf)>data_size):
        data = voice_data_buf[0:data_size]
        voice_data_buf = voice_data_buf[data_size:]
        return data
    else:
        return b''

def recv_voice_data():
    while True:
        data, addr = receive_socket.recvfrom(5000)
        insert_data_tobuff(data)

# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws):
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args):
        frameSize = 640  # 每一帧的音频大小
        intervel = 0.04  # 发送音频间隔(单位:s)
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

        # CHUNK = 5120#队列长度
        # FORMAT = pyaudio.paInt16 #保存格式
        # CHANNELS = 1  #几个通道
        # RATE = 8000 #采样率，一般8000的采样率能识别出人说的话
        # record_p = pyaudio.PyAudio() #实例化
        # #打开获取流
        # stream = record_p.open(format=FORMAT,
        #         channels=CHANNELS,
        #         rate=RATE,
        #         output=True,
        #         frames_per_buffer=CHUNK)
    
        

        while True:
            buf = get_data(640)
            # 文件结束
            if not buf:
                status = STATUS_LAST_FRAME
            # 第一帧处理
            # 发送第一帧音频，带business 参数
            # appid 必须带上，只需第一帧发送
            if status == STATUS_FIRST_FRAME:

                d = {"common": wsParam.CommonArgs,
                    "business": wsParam.BusinessArgs,
                    "data": {"status": 0, "format": "audio/L16;rate=8000",
                            "audio": str(base64.b64encode(buf), 'utf-8'),
                            "encoding": "raw"}}
                d = json.dumps(d)
                ws.send(d)
                status = STATUS_CONTINUE_FRAME
            # 中间帧处理
            elif status == STATUS_CONTINUE_FRAME:
                d = {"data": {"status": 1, "format": "audio/L16;rate=8000",
                            "audio": str(base64.b64encode(buf), 'utf-8'),
                            "encoding": "raw"}}
                ws.send(json.dumps(d))
            # 最后一帧处理
            elif status == STATUS_LAST_FRAME:
                d = {"data": {"status": 2, "format": "audio/L16;rate=8000",
                            "audio": str(base64.b64encode(buf), 'utf-8'),
                            "encoding": "raw"}}
                ws.send(json.dumps(d))
                time.sleep(1)
                break
            # 模拟音频采样间隔
            time.sleep(intervel)
        ws.close()
        
    thread_voice = threading.Thread(target=recv_voice_data,args=())
    thread_voice.start()
    thread_test = threading.Thread(target=run,args=())
    thread_test.start()

if __name__ == "__main__":
    # 测试时候在此处正确填写相关信息即可运行
    time1 = datetime.now()
    wsParam = Ws_Param(APPID='35dcd3b2', APISecret='YmE0MjExMmJhY2IxMjE3MTIzMmI4NDVk',
                       APIKey='f3a9201fdb7ba85e1a2d249168fc5c72',
                       AudioFile=r'E:\1230.wav')
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    time2 = datetime.now()
    print(time2-time1)
