import socket
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import time
import requests
import json
import cv2
from error_dialog import message_Dialog

import robot_api

# {
#     "method":"Get",
#     "url":"init",
#     "param":{}
# }

# [
#     {"method":"Get",
#     "url":"init",
#     "param":{}},
#     {"method":"Post",
#     "url":"init",
#     "param":{}}
# ]

# 生成一个http请求参数字典
def creat_request_param(method, url, param = {},loop = False):
    param_dict = {}
    param_dict["method"] = method
    param_dict["url"] = url
    param_dict["param"] = param
    param_dict["loop"] = loop
    return param_dict


# wait_timeout 请求超时等待的最大时间
# time_interval 两次请求之间的间隔
class http_request_Thread(QThread): # 发送http 请求
    signal = pyqtSignal(requests.Response) #设置触发信号传递的参数数据类型,这里是字符串
    def __init__(self, request_params , wait_timeout = 5 , time_interval = 1):
        super(http_request_Thread, self).__init__()
        self.request_params = request_params
        self.headers = {
        "Content-Type": "application/json",
        "Connection": "close",
        }
        self.wait_timeout = wait_timeout
        self.time_interval = time_interval
    # 向服务器发送get请求
    # 调用关联函数，返回服务器返回数据
    def HandleOnceGetRequest(self, url, param):
        try:
            if param:
                response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API[url]}", 
                                        params= param,
                                        timeout=self.wait_timeout)
            else:
                response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API[url]}", 
                                        timeout=self.wait_timeout)
            self.signal.emit(response)
        except Exception as e:
            print("GetRequest:" , e)
            return
    # 向服务器发送post请求
    # 调用关联函数，返回服务器返回数据
    def HandleOncePostRequest(self, url, param):
        try:
            response = requests.post(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API[url]}", 
                                    data=json.dumps(param),  #dumps参数为字典，dump参数为文件指针
                                    headers=self.headers, 
                                    timeout=self.wait_timeout)
            self.signal.emit(response)
        except Exception as e:
            print("PostRequest:" , e)
            return
    #处理一次请求发送，根据不同参数发送不同的请求
    def HandleOnceRequest(self, request_param):
        try:
            if request_param["method"] == "Get":
                self.HandleOnceGetRequest(request_param["url"], request_param["param"])
            elif request_param["method"] == "Post":
                self.HandleOncePostRequest(request_param["url"],request_param["param"])
            else:
                print("http request method error")
        except Exception as e:
            print("HandleRequest:" , e)

    def run(self): #线程运行函数
        if type(self.request_params) == dict:    #只发送一次请求就可以
            if not self.request_params["loop"]:
                self.HandleOnceRequest(self.request_params)
            else:
                while True:
                    self.HandleOnceRequest(self.request_params)
                    time.sleep(self.time_interval)
        elif type(self.request_params) == list:   #发送多个请求
            try:
                for request_param in self.request_params:
                    self.HandleOnceRequest(request_param)
                    if self.time_interval != 0:
                        self.sleep(self.time_interval)
            except Exception as e:
                print("request params list error" , e)
        else:
            print("request params type error")


class message_display_Thread(QThread): # 显示收到的错误或者消息
    def __init__(self,message_type,message):
        super(message_display_Thread, self).__init__()
        self.message_type = message_type
        self.message = message


    def run(self): 
            try:
                dialog = message_Dialog(self.message_type,self.message)
                result = dialog.exec_()
            except Exception:
                return

# 接收内部ip通过socket传送的视频音频数据
class message_receive_Thread(QThread):
    signal = pyqtSignal(bytes)  #设置触发信号传递的参数数据类型,这里是字符串
    def __init__(self,host,port):
        super(message_receive_Thread, self).__init__()
        self.host= host
        self.port= port 

    def run(self): 
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #udp
        self.receive_socket.bind((self.host, self.port))
        while True:
            try:
                data, addr = self.receive_socket.recvfrom(65000)
                self.signal.emit(data)
            except Exception as e:
                continue
