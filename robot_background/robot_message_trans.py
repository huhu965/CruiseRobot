import socket
import sys
import threading
import time
import struct
import requests
import json
import os
import datetime
from threading import Thread
from client_socket import Client_Socket
from web_socket import robot_device_status_update_Thread, robot_navigate_status_update_Thread
from gs_robot.robot_thread_class import *
from gs_robot.general_function import Param_Init
from gs_robot.cmd import open_video, close_video
from play_voice import PlayVoice, play_system_audio
from handle_awake import RobotAwakeProcess
#用于机器人工控机的，把来自服务器的请求转一次发送给导航系统
#再将导航系统的返回值转发给服务器
#链接的心跳检测类
#心跳包的发送
#断线重连
class heart_send_Thread(Thread): # socket接收消息线程
    def __init__(self,request_process):
        super(heart_send_Thread, self).__init__()
        self.request_process = request_process

    def run(self): # 在启动线程后任务从这个函数里面开始执行
        while True:
            #链接了但是15秒都没有收到消息，就发送心跳包去给服务器
            if (datetime.datetime.now() - self.request_process.last_receive_time).seconds > 15  and self.request_process.socket_link_flag:
                self.request_process.send_heart_message()
            #链接了，发送了心跳包都没有回应，就认为链接已经被服务器关掉了
            if (datetime.datetime.now() - self.request_process.last_receive_time).seconds > 35 and self.request_process.socket_link_flag:
                self.request_process.close_link()
                #重新链接
                self.request_process.connect_server()
                self.request_process.register_identity()
            time.sleep(5)

class robot_client_message_process(Client_Socket,Param_Init):
    def __init__(self,server_ip):
        Param_Init.__init__(self)
        Client_Socket.__init__(self,server_ip)
        self.robot_ip = '10.7.5.88' #机器人的内网地址
        self.robot_port = 8080
        self.cmd_ip = ('127.0.0.1', 8002) #本地云台指令接收地址
        self.headers = {
        "Content-Type": "application/json",
        "Connection": "close",
        }
        self.methods = ["POST","GET"]
        #print(f"主进程{os.getpid()}")
        self.cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #udp,给摄像头那边发送指令
        #心跳线程
        self.heart_thread = heart_send_Thread(self)
        #更新机器人状态线程
        self.robot_status_update_thread = robot_device_status_update_Thread(("10.7.5.88",8089))
        #更新机器人导航状态线程
        self.robot_navigate_status_update_thread = robot_navigate_status_update_Thread(("10.7.5.88",8089))
        #状态检查线程
        self.status_check_thread = status_check_Thread(self)
        self.robot_position_update_thread = robot_position_update_Thread()
        #提交数据线程
        self.robot_device_data_upload_thread = robot_device_data_upload_Thread(self,("101.37.16.240",62223))
        #获取声音线程
        self.robot_awake_process = RobotAwakeProcess(("127.0.0.1",8020))


    #链接成功后向服务器部分注册自己的身份
    def register_identity(self):
        if self.socket_link_flag:
            content = b"robot_client \r\n"
            self.recv_socket.sendall(content)
    #接收服务器传过来的数据
    #服务器传数据会先传一个数据结构过来，存放即将传输的数据大小
    def receive_request(self):
        try:
            if self.socket_link_flag:
                _size = struct.calcsize('I')
                fhead = self.recv_socket.recv(_size,0x100)  #0x100在c++中代表接收waitall
                #处理接收长度信息
                if len(fhead) == 0: #基本上是服务器端关闭了，拖着等重连启动
                    return b''
                else:  #接收到任何消息都可以作为心跳的回应，认为链接仍在
                    print("xi")
                    self.update_last_receive_time()
                length, = struct.unpack('I', fhead)
                if length == 0:
                    return b''
                else:
                    data = self.recv_socket.recv(length,0x100)  #接收服务器发的请求
                    return data
            else:
                return b''
        except Exception as e:
            return b''

    #发送响应信息
    #发送两条信息，一条是数据大小，一条是数据
    def respond_send(self,back_data):
        fhead = struct.pack('I',len(back_data)) 
        try:
            self.lock.acquire()
            self.recv_socket.send(fhead) 
            self.recv_socket.sendall(back_data)
        except Exception as e:
            print("SEND err",e)
        finally:
            self.lock.release()
    #处理post请求
    #url 请求方法
    #post_data post请求提交的数据
    def handle_post_request(self, url, post_data):
        try:
            response = requests.post(f"http://{self.robot_ip}:{self.robot_port}{url}", 
                        data=post_data,  #dumps直接给字典，dump要给文件指针
                        headers=self.headers, timeout=3)

            back_data = self.respond_message_creat(content=response.content)
        except Exception as e:
            back_data = self.respond_message_creat(errorCode =f"post request error:{e}" ,msg = "fail", successed= False)
        finally:
            return back_data   
    #处理get请求
    #url 请求方法
    def handle_get_request(self, url):
        try:
            response = requests.get(f"http://{self.robot_ip}:{self.robot_port}{url}", timeout=3)
            back_data = self.respond_message_creat(content=response.content)
        except Exception as e:
            back_data = self.respond_message_creat(errorCode = f"get request error:{e}",msg = "fail", successed= False)
        finally:
            return back_data

    def POST(self, request_data):
        try:#分割url
            request_head = request_data.decode("utf-8").split("\r\n")[0]
            url = request_head.split(' ')[1]
            if '?' in url:
                url_cmd, url_param = url.split('?') #拆分url
            else:
                url_cmd = url
                url_param = ""
            space, name, modules, func = url_cmd.split("/")
        except Exception as e:
            back_data = self.respond_message_creat(msg = f"post url error:{e}")
            self.respond_send(back_data)
            return
        #根据请求指令进行处理
        try:
            obj = __import__("gs_robot." + modules, fromlist=True)  # 注意fromlist参数
            if hasattr(obj, func):
                func = getattr(obj, func)
                back_data = func(self, request_data.split(b'\r\n\r\n')[1])
            else:
                back_data = self.handle_post_request(url = url, post_data = request_data.split(b'\r\n\r\n')[1])
        except Exception as e:
            back_data = self.respond_message_creat(msg = f"modules handle error:{e}")
        finally:
            self.respond_send(back_data)

    def GET(self, request_data):
        try:#分割url
            request_head = request_data.decode("utf-8").split("\r\n")[0]
            url = request_head.split(' ')[1]
            if '?' in url:
                url_cmd, url_param = url.split('?') #拆分url
            else:
                url_cmd = url
                url_param = ""
            space, name, modules, func = url_cmd.split("/")
        except Exception as e:
            back_data = self.respond_message_creat(msg = f"get url error:{e}")
            self.respond_send(back_data)
            return
        #根据请求指令进行处理
        try:
            obj = __import__("gs_robot." + modules, fromlist=True)  # 注意fromlist参数
            if hasattr(obj, func):
                func = getattr(obj, func)
                back_data = func(self, url_param)
            else: #其他的导航请求
                # back_data = self.respond_message_creat()
                back_data = self.handle_get_request(url = url)
        except Exception as e:
            back_data = self.respond_message_creat(msg = f"modules handle error:{e}")
        finally:
            self.respond_send(back_data)
    #处理请求
    def process_request(self, request_data):
        #提取url和method
        request_head = request_data.decode("utf-8").split("\r\n")[0]
        method  = request_head.split(' ')[0]

        if method in self.methods:
            func = getattr(self, method)
            func(request_data)
        else:
            back_data = self.respond_message_creat(msg = "method name error")
            self.respond_send(back_data)
    #运行
    def run(self):
        self.heart_thread.start()
        self.robot_status_update_thread.start()
        self.robot_navigate_status_update_thread.start()
        self.robot_position_update_thread.start()
        self.status_check_thread.start()
        self.robot_device_data_upload_thread.start()
        self.robot_awake_process.start()

        self.connect_server()
        self.register_identity()#注册身份
        time.sleep(2)
        play_system_audio('初始化完成')
        # open_video(self, robot_usr = True ) #打开视频
        while True:
            try:
                request_data = self.receive_request()
                # print(request_data)
                if len(request_data) == 0:
                    time.sleep(2)
                    continue
                else:
                    self.process_request(request_data)
            except Exception as e:
                print(e)
        close_video(self, robot_usr = True)
        self.recv_socket.close()

def main():
    play_system_audio('开始初始化')
    # time.sleep(140)
    server_ip =  ('101.37.16.240', 62222)#服务器的公网地址和端口
    request_process = robot_client_message_process(server_ip)
    request_process.run()

if __name__ == '__main__':
    main()

    
