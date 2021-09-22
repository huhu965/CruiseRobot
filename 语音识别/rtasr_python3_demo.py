# -*- encoding:utf-8 -*-

import sys
import hashlib
from hashlib import sha1
import hmac
import base64
from socket import *
import json, time, threading
from websocket import create_connection
import websocket
from urllib.parse import quote
import logging
import os
import pyaudio
import wave

# reload(sys)
# sys.setdefaultencoding("utf8")
logging.basicConfig()

pd = "edu"

end_tag = "{\"end\": true}"


class Client():
    def __init__(self):
        base_url = "ws://rtasr.xfyun.cn/v1/ws"
        app_id = "35dcd3b2"
        api_key = "4ecffbda7f4ee1a993137808755daf51"

        ts = str(int(time.time()))
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')

        self.ws = create_connection(base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa))
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()

    def send(self, file_path):
        CHUNK = 5120#队列长度
        FORMAT = pyaudio.paInt16 #保存格式
        CHANNELS = 1  #几个通道
        RATE = 16000 #采样率，一般8000的采样率能识别出人说的话
        record_p = pyaudio.PyAudio() #实例化
        #打开获取流
        stream = record_p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
        try:
            while True:
                chunk = stream.read(1280)
                if not chunk:
                    break
                self.ws.send(chunk)

                time.sleep(0.04)
        finally:
            pass

        self.ws.send(bytes(end_tag.encode('utf-8')))
        print("send end tag success")

    def recv(self):
        try:
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    print("receive result end")
                    break
                result_dict = json.loads(result)
                # 解析结果
                if result_dict["action"] == "started":
                    print("handshake success, result: " + result)

                if result_dict["action"] == "result":
                    result_1 = result_dict
                    # print("rtasr result: " + result_1["data"])
                    res_dict = json.loads(result_1["data"])
                    if res_dict["cn"]["st"]["type"] == "0": #0是最终结果，1是中间结果
                        result_cn = ""
                        result_list = res_dict["cn"]["st"]["rt"][0]["ws"] #列表，包含结果
                        for result in result_list:
                            if result["cw"][0]["wp"] =="s":
                                print(result["cw"][0]["w"])
                            else:
                                result_cn += result["cw"][0]["w"]
                        print(result_cn)

                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return
        except websocket.WebSocketConnectionClosedException:
            print("receive result end")

    def close(self):
        self.ws.close()
        print("connection closed")


if __name__ == '__main__':
    client = Client()
    client.send(file_path)
