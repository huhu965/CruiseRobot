import socket
import os
import sys
import threading
import time
import datetime
import json
import serial
import requests
from threading import Thread
from client_socket import Client_Socket
import websocket
from multiprocessing import Process, Queue

#读取气体浓度
class gasConcentration_Thread(Thread):
    def __init__(self):
        super(gasConcentration_Thread, self).__init__()
        self.actual_data1 = 0
        self.actual_data2 = 0

    def run(self): # 在启动线程后任务从这个函数里面开始执行
        data = b''
        # print(f"气体浓度 子进程{os.getpid()} 开始执行，父进程为{os.getppid()}")
        while True:
            try:
                ser=serial.Serial("/dev/ttyUSB0",9600,timeout=0.5) #使用USB连接串行口
                cmd = '01 04 00 00 00 08 F1 CC' #读数据命令

                while True:
                    read_cmd = bytes.fromhex(cmd) #转为16进制
                    ser.write(read_cmd)
                    data= ser.readall() 
                    read_data1 =int.from_bytes(data[3:5],byteorder='big',signed=False)
                    read_data2 =int.from_bytes(data[5:7],byteorder='big',signed=False)
                    self.actual_data1 = round((read_data1 - 832)*100/(4096-832))
                    self.actual_data2 = round((read_data2 - 832)*100/(4096-832))
                    time.sleep(1)
                ser.close()
            except Exception as e:
                time.sleep(2)
                continue

    def get_data(self):
        if self.actual_data1 < 0:
            self.actual_data1 = 0
        if self.actual_data2 < 0:
            self.actual_data2 = 0   
        return {"sensor1":self.actual_data1,"sensor2":self.actual_data2}

class robot_status_heart_Thread(Thread): #机器人状态链接心跳线程
    def __init__(self,main_process):
        super(robot_status_heart_Thread, self).__init__()
        self.main_process = main_process

    def run(self): # 在启动线程后任务从这个函数里面开始执行
        while True:
            #链接了，发送了心跳包都没有回应，就认为链接已经被服务器关掉了
            if (datetime.datetime.now() - self.main_process.last_receive_time).seconds > 35 and self.main_process.socket_link_flag:
                self.main_process.close_link()
                #重新链接
                self.main_process.connect_server()
                self.register_to_server()
            time.sleep(5)
#websocket,机器人会自动推送状态信息等
# "GET /gs-robot/notice/system_health_status HTTP/1.1\r\n
# Host: 10.7.5.88:8089\r\n
# Upgrade: websocket\r\n
# Connection: Upgrade\r\n
# Sec-WebSocket-Key: 42qlQSy1wUUqaq2veduEbQ==\r\n\r\n"

# robot_ip = '10.7.5.88' #机器人的内网地址
# robot_port = 8089
# 获取推送，更新状态
class robot_device_status_update_Thread(Thread, Client_Socket):
    def __init__(self, server_ip):
        #父类初始化
        Thread.__init__(self)
        Client_Socket.__init__(self,server_ip)
        #自己的初始化
        self.visit_data_lock = threading.Lock()
        self.request = {
        "Url": "GET /gs-robot/notice/device_status HTTP/1.1",
        "Host": "Host: 10.7.5.88:8089",
        "Upgrade": "Upgrade: websocket",
        "Connection": "Connection: Upgrade",
        "Sec-WebSocket-Key": "Sec-WebSocket-Key: 42qlQSy1wUUqaq2veduEbQ==",}
        self.robot_device_status_dict = {}

        self.gasConcentration_thread = gasConcentration_Thread()
        self.gasConcentration_thread.start()

        self.heart_thread = robot_status_heart_Thread(self)
        self.heart_thread.start()
    #链接web_socket服务器
    def register_to_server(self):
        #链接成功后向服务器发送命令
        web_socket_request = (f"{self.request['Url']}\r\n"
                            + f"{self.request['Host']}\r\n"
                            + f"{self.request['Upgrade']}\r\n"
                            + f"{self.request['Connection']}\r\n"
                            + f"{self.request['Sec-WebSocket-Key']}\r\n\r\n").encode()
        self.recv_socket.send(web_socket_request)
        respond = self.recv_socket.recv(5000)
    #系统硬件状态
    #b'\x81~\x01+
    # {"autoMode":false,
    # "battery":77, 电池电量
    # "charger":0, 充电状态
    # "chargerCurrent":0,
    # "chargerVoltage":0,
    # "emergency":false, 急停
    # "emergencyStop":false, 急停 上一个参数相或
    # "locationStatus":false,定位状态
    # "navigationSpeedLevel":2, 导航速度
    # "speed":0, 实时速度
    #更新数据
    def update_data(self,data):
        try:
            device_status = json.loads(data[4:-1]) #从json里恢复字典
            concentration_data = self.gasConcentration_thread.get_data()
            self.visit_data_lock.acquire()
            self.robot_device_status_dict['battery'] = device_status['battery']
            self.robot_device_status_dict['charger'] = device_status['charger']
            self.robot_device_status_dict['emergency'] = device_status['emergency']
            self.robot_device_status_dict['emergencyStop'] = device_status['emergencyStop']
            self.robot_device_status_dict['locationStatus'] = device_status['locationStatus']
            self.robot_device_status_dict['navigationSpeedLevel'] = device_status['navigationSpeedLevel']
            self.robot_device_status_dict['speed'] = device_status['speed']
            self.robot_device_status_dict['sensor1'] = concentration_data['sensor1']
            self.robot_device_status_dict['sensor2'] = concentration_data['sensor2']
        except Exception as e:
            print("stat",e)
        finally:
            self.visit_data_lock.release()

    #返回数据
    def get_data(self):
        try:
            return self.robot_device_status_dict
        except Exception:
            return False

    def run(self):
        self.connect_server()
        self.register_to_server()
        while True:
            try:
                status_data = self.recv_socket.recv(5000)
                self.update_last_receive_time()
                self.update_data(status_data)
            except Exception as e:
                print(e)
#获取导航状态信息
class robot_navigate_status_update_Thread(Thread, Client_Socket):
    def __init__(self, server_ip):
        #父类初始化
        Thread.__init__(self)
        Client_Socket.__init__(self,server_ip)
        #自己的初始化
        self.visit_data_lock = threading.Lock()
        self.robot_navigate_status_dict = {}
        self.robot_navigate_status_dict['noticeTypeLevel'] = ''
        self.robot_navigate_status_dict['noticeType'] = ''
        self.robot_navigate_status_dict['noticeDataFields'] = ''
        self.robot_navigate_status_dict['name'] = ''
        self.navigate_status = ''
        self.request = {
        "Url": "GET /gs-robot/notice/navigation_status HTTP/1.1",
        "Host": "Host: 10.7.5.88:8089",
        "Upgrade": "Upgrade: websocket",
        "Connection": "Connection: Upgrade",
        "Sec-WebSocket-Key": "Sec-WebSocket-Key: 42qlQSy1wUUqaq2veduEbQ==",}
    #链接web_socket服务器
    def register_to_server(self):
        #链接成功后向服务器发送命令
        web_socket_request = (f"{self.request['Url']}\r\n"
                            + f"{self.request['Host']}\r\n"
                            + f"{self.request['Upgrade']}\r\n"
                            + f"{self.request['Connection']}\r\n"
                            + f"{self.request['Sec-WebSocket-Key']}\r\n\r\n").encode()
        self.recv_socket.send(web_socket_request)
        respond = self.recv_socket.recv(5000) #读取导航服务器返回的信息

    #系统硬件状态
    #b'\x81~\x015
    # {"noticeTypeLevel":INFO or WARN  通知等级，是日常通知还是警告
    # "noticeType": LOCALIZATION_FAILED定位失败，REACHED 到达目的地，PLANNING 正在规划，HEADING 正在前往目的地，UNREACHED到达目的地，但有障碍物，
    # "noticeDataFields":tye类型字段的说明，可以忽略
    def update_data(self,data):
        self.visit_data_lock.acquire()
        try:
            data_list = data.split(b'\n')
            navigate_status = json.loads(data_list[-2][4:])#取最近的一次数据
            self.robot_navigate_status_dict['noticeTypeLevel'] = navigate_status['noticeTypeLevel']
            self.robot_navigate_status_dict['noticeType'] = navigate_status['noticeType']
            self.robot_navigate_status_dict['noticeDataFields'] = navigate_status['noticeDataFields']
            if self.navigate_status == '':
                if  navigate_status['noticeType'] == 'PLANNING' or navigate_status['noticeType'] == 'HEADING':
                    self.navigate_status = 'navigate_running'
                else:
                    self.navigate_status = 'navigate_end'
            elif self.navigate_status == 'navigate_running':
                if  navigate_status['noticeType'] == 'REACHED' or navigate_status['noticeType'] == 'UNREACHED':
                    self.navigate_status = 'navigate_end'
        except Exception:
            self.robot_navigate_status_dict['noticeType'] = "error"
        finally:
            self.visit_data_lock.release()
    #初始化导航状态
    def init_navigate_status(self):
        self.navigate_status = ''
    #给外部返回导航状态的接口
    def get_navigate_status(self):
        return self.navigate_status
    #返回数据
    def get_data(self):
        try:
            return self.robot_navigate_status_dict
        except Exception:
            return False
    #线程运行
    def run(self):
        # print(f"导航状态 子进程{os.getpid()} 开始执行，父进程为{os.getppid()}")
        self.connect_server()
        self.register_to_server()
        while True:
            try:
                status_data = self.recv_socket.recv(5000)
                self.update_last_receive_time()
                self.update_data(status_data)
            except Exception as e:
                print(e)