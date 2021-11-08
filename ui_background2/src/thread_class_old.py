import socket
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import time
import requests
import json
import cv2
from error_dialog import message_Dialog

import robot_api

class load_map_Thread(QThread): # 发送http get请求
    signal = pyqtSignal(requests.Response) #设置触发信号传递的参数数据类型,这里是字符串
    def __init__(self, map_name):
        super(load_map_Thread, self).__init__()
        self.map_name = map_name

    def run(self): # 在启动线程后任务从这个函数里面开始执行
            try:
                # #初始化位置
                param = {"map_name":self.map_name,"init_point_name":"Current"}
                response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['initialize_directly']}", params=param, timeout=5)
                print(response.content)
                response_message = json.loads(response.content) #从json里恢复字典
                if response_message["successed"] != True:
                    dialog = message_Dialog("error_init_pos",response.content)
                    result = dialog.exec_()
                    return
            except requests.exceptions.RequestException as e:
                print(e)
            except Exception as e:
                print(e)

class request_send_Thread(QThread): # 发送http get请求
    signal = pyqtSignal(requests.Response) #设置触发信号传递的参数数据类型,这里是字符串
    def __init__(self,url,param = ""):
        super(request_send_Thread, self).__init__()
        self.param = param
        self.url = url


    def run(self): # 在启动线程后任务从这个函数里面开始执行
            try:
                if self.param == "":
                    response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API[self.url]}", timeout=5)
                else:
                    response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API[self.url]}", self.param, timeout=5)
                self.signal.emit(response)
            except Exception:
                return

class post_request_send_Thread(QThread): # 发送post请求
    signal = pyqtSignal(requests.Response) #设置触发信号传递的参数数据类型,这里是字符串
    def __init__(self,url,param = ""):
        super(post_request_send_Thread, self).__init__()
        self.param = param
        self.url = url
        self.headers = {
        "Content-Type": "application/json",
        "Connection": "close",
        }

    def run(self): # 在启动线程后任务从这个函数里面开始执行
        # while True:
            try:
                response = requests.post(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API[self.url]}", 
                                        data=json.dumps(self.param),  #dumps直接给字典，dump要给文件指针
                                        headers=self.headers, timeout=5)
                self.signal.emit(response)
            except Exception as e:
                return

class message_display_Thread(QThread): # 显示收到的错误或者消息
    def __init__(self,message_type,message):
        super(message_display_Thread, self).__init__()
        self.message_type = message_type
        self.message = message


    def run(self): # 在启动线程后任务从这个函数里面开始执行
            try:
                dialog = message_Dialog(self.message_type,self.message)
                result = dialog.exec_()
            except Exception:
                return

class message_receive_Thread(QThread): # socket接收消息线程
    signal = pyqtSignal(bytes) #设置触发信号传递的参数数据类型,这里是字符串
    def __init__(self,host,port):
        super(message_receive_Thread, self).__init__()
        self.host= host
        self.port= port 

    def run(self): # 在启动线程后任务从这个函数里面开始执行
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)# SOCK_STREAM SOCK_DGRAM
        self.receive_socket.bind((self.host, self.port))
        while True:
            try:
                data, addr = self.receive_socket.recvfrom(65000)
                self.signal.emit(data)
            except Exception as e:
                break

class robot_current_position_Thread(QThread): # 发送http get请求
    signal = pyqtSignal(dict) #设置触发信号传递的参数数据类型,这里是字符串
    def __init__(self):
        super(robot_current_position_Thread, self).__init__()

    def run(self): # 在启动线程后任务从这个函数里面开始执行
        while True:#等初始化完才能获取坐标点
            try:
                response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['is_initialize_finished']}", timeout=5)
                response_message = json.loads(response.content) #从json里恢复字典
                print(response_message)
                if response_message["successed"] != True:
                    self.sleep(10)
                    continue
                if response_message["data"] == "true" or response_message['data'] == '':
                    self.initialize_robot_finish = True
                    break
                self.sleep(10)
            except Exception:
                self.sleep(10)
        while True:
            try:
                response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['position']}", timeout=5)
                response_message = json.loads(response.content) #从json里恢复字典
                self.signal.emit(response_message)
                time.sleep(2) #休眠两秒，然后在请求机器人位置
            except Exception as e:
                print(e)
                self.sleep(10)

class robot_scan_mode_Thread(QThread): # 发送http get请求
    def __init__(self,map_name,param):
        super(robot_scan_mode_Thread, self).__init__()
        self.map_name = map_name
        self.param = param

    def run(self): # 在启动线程后任务从这个函数里面开始执行
        headers = {
        "Content-Type": "application/json",
        }
        try:
            response = requests.post(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['start_task_queue']}", 
                                    data=json.dumps(self.param),  #dumps直接给字典，dump要给文件指针
                                    headers=headers, timeout=5)
            print(response.content)
        except Exception as e:
            print(e)
            return
                
class robot_data_receive_Thread(QThread): # 发送http get请求
    signal = pyqtSignal(dict) #设置触发信号传递的参数数据类型,这里是字符串
    def __init__(self):
        super(robot_data_receive_Thread, self).__init__()

    def run(self): # 在启动线程后任务从这个函数里面开始执行
        while True:
            try:
                response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['device_status']}", timeout=5)
                status_dict = json.loads(response.content) #从json里恢复字典
                if status_dict["successed"] != True:
                    self.signal.emit({'successed':False,'errorCode':"link_error"})
                    self.sleep(10)
                    continue
                self.signal.emit(status_dict)
                time.sleep(2) #休眠1秒，然后请求机器人状态
            except Exception as e:
                print(e)
                self.signal.emit({'successed':False,'errorCode':"link_error"})
                self.sleep(10)

class robot_navigate_back_Thread(QThread): # 发送http get请求
    signal = pyqtSignal(requests.Response) #设置触发信号传递的参数数据类型,这里是字符串
    def __init__(self):
        super(robot_navigate_back_Thread, self).__init__()

    def run(self): # 在启动线程后任务从这个函数里面开始执行
        try:
            response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['cancle_task_queue']}", timeout=5)
        except Exception:
            return
        try:
            param = {"map_name":"factoryall","position_name":"厂区出口"}
            response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['navigate']}", param ,timeout=5)
            self.signal.emit(response)
        except Exception as e:
            return

class robot_video_refush_Thread(QThread): # 发送http get请求
    def __init__(self):
        super(robot_video_refush_Thread, self).__init__()

    def run(self): # 在启动线程后任务从这个函数里面开始执行
        try:
            response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['close_video']}", timeout=5)
        except Exception as e:
            print(e)
        time.sleep(4)
        try:
            response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['open_video']}",timeout=5)
        except Exception as e:
            print(e)
            return
