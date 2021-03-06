# /* 
# * @Author: Hu Ziwei
#  * @Date: 2021-07-06 23:46:54
#  * @Last Modified by: Hu Ziwei
#  * @Last Modified time: 2021-07-06 23:46:54 
# */
#添加了两台机器人同时链接的支持
#暂不支持任意多台机器人同时链接，未来重新改架构再说
import socketserver
import threading
import time
import re
import socket
import sys
import struct
import datetime
from threading import Thread
import json
import redis
socket_dict = {} #存socket链接的
robot_tcp_use_lock = threading.Lock()
cz_robot_tcp_use_lock = threading.Lock()
redis_db = redis.Redis(host='127.0.0.1', port=6379, db=0,decode_responses=True)

class RecviveRobotData(Thread):
    def __init__(self,ip_port):
        super(RecviveRobotData, self).__init__()
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #udp
        self.receive_socket.bind(ip_port)
    def run(self):
        while True:
            try:
                data, addr = self.receive_socket.recvfrom(2000)
                data_str = data.decode('utf-8')
                if data_str.endswith('\r\n\r\n'):
                    data_dict = json.loads(data_str[:-4])#反序列化
                else:
                    continue
                redis_db.set(data_dict["time"],data_str[:-4]) #所有数据存储起来
                redis_db.hset("last_status", "last_status_data", data_str[:-4])#每次更新
            except Exception as e:
                print("RecviveRobotData:",e)
                time.sleep(1)
        self.receive_socket.shutdown(2)
        self.receive_socket.close()

class RecviveRobotVideoNormal(Thread): #接收彩色视频
    def __init__(self):
        super(RecviveRobotVideoNormal, self).__init__()
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #udp
        host = socket.gethostname()
        self.receive_socket.bind((host,62220))
        self.last_stamp = 0
        self.target_client_identify = "soft_video"

    def run(self):
        global socket_dict
        while True:
            try:
                data, addr = self.receive_socket.recvfrom(10000)
                stamp, = struct.unpack('I', data[0:4]) #解算时间戳
                if stamp >= self.last_stamp:
                    self.last_stamp = stamp
                    if len(data) > 4 and (self.target_client_identify in socket_dict.keys()): #不只有时间戳，还有数据
                        fhead = struct.pack('II',2,len(data)-4)
                        socket_dict[self.target_client_identify].request.send(fhead)
                        socket_dict[self.target_client_identify].request.sendall(data[4:])
                elif stamp < (self.last_stamp - 15): #如果时间戳小于之前的15次，可以认为是一次新的信息传输
                    self.last_stamp = stamp
            except Exception as e:
                print("RecviveRobotVideoNormal:",e)
                time.sleep(1)
        self.receive_socket.shutdown(2)
        self.receive_socket.close()
        

class RecviveRobotVideoInfrared(Thread): #接收彩色视频
    def __init__(self):
        super(RecviveRobotVideoInfrared, self).__init__()
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #udp
        host = socket.gethostname()
        self.receive_socket.bind((host,62221))
        self.last_stamp = 0
        self.target_client_identify = "soft_video_red"

    def run(self):
        global socket_dict
        while True:
            try:
                data, addr = self.receive_socket.recvfrom(10000)
                stamp, = struct.unpack('I', data[0:4]) #解算时间戳
                if stamp >= self.last_stamp:
                    self.last_stamp = stamp
                    if len(data) > 4 and (self.target_client_identify in socket_dict.keys()): #不只有时间戳，还有数据
                        fhead = struct.pack('II',2,len(data)-4)
                        socket_dict[self.target_client_identify].request.send(fhead)
                        socket_dict[self.target_client_identify].request.sendall(data[4:])
                elif stamp < (self.last_stamp - 15): #如果时间戳小于之前的15次，可以认为是一次新的信息传输
                    self.last_stamp = stamp
            except Exception as e:
                print("RecviveRobotVideoInfrared:",e)
                time.sleep(1)
        self.receive_socket.shutdown(2)
        self.receive_socket.close()

class RobotLink:
    lock = threading.Lock()
    robot_tcp = None
    robot_tcp_link = False
    
    cz_robot_tcp = None
    cz_robot_tcp_link = False
    #根据客户端链接发送的信息 
    #注册不同的身份
    #用于不同的处理
    @classmethod
    def join(cls, client):
        global socket_dict   #tcp链接存储
        global robot_tcp_use_lock
        global cz_robot_tcp_use_lock
        with cls.lock:
            if client.method == "robot_client":
                if not cls.robot_tcp_link:
                    cls.robot_tcp = client #记录下机器人客户端
                    cls.robot_tcp_link = True
                    client.identity = 'robot'
                    client.robot_keep_live = cls.robot_tcp_link
                    client.robot_tcp_lock_ = robot_tcp_use_lock
                    val = struct.pack("QQ", 3,0)
                    client.request.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, val)#设置接收超时链接
                elif cls.robot_tcp_link:
                    client.identity = 'error'
                    print("等待关闭之前链接")
                    
            if client.method == "cz_robot":
                if not cls.cz_robot_tcp_link:
                    cls.cz_robot_tcp = client #记录下机器人客户端
                    cls.cz_robot_tcp_link = True
                    client.identity = 'cz_robot'
                    client.robot_keep_live = cls.cz_robot_tcp_link
                    client.robot_tcp_lock_ = cz_robot_tcp_use_lock
                    val = struct.pack("QQ", 3,0)
                    client.request.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, val)#设置接收超时链接
                elif cls.cz_robot_tcp_link:
                    client.identity = 'error'
                    print("等待关闭之前链接")

            elif client.method == "GET" or client.method == "POST":
                client.identity = "user"
                if client.request_data.decode().split(' ')[1].startswith("/cz_robot"):
                    client.robot_tcp = cls.cz_robot_tcp
                    client.robot_keep_live = cls.cz_robot_tcp_link
                    client.robot_tcp_lock_ = cz_robot_tcp_use_lock
                else:
                    client.robot_tcp = cls.robot_tcp
                    client.robot_keep_live = cls.robot_tcp_link
                    client.robot_tcp_lock_ = robot_tcp_use_lock

            elif client.method in socket_dict.keys():
                socket_dict[client.method].request.close()#关闭上一个链接
                del socket_dict[client.method]
                #重新添加
                socket_dict[client.method] = client
                client.identity = client.method

            else: 
                socket_dict[client.method] = client
                client.identity = client.method
            
    #用于处理机器人链接断开后的链接释放
    @classmethod
    def close_link(cls, cz_robot):
        with cls.lock:
            if cz_robot:
                cls.cz_robot_tcp = None
                cls.cz_robot_tcp_link = False
            else:
                cls.robot_tcp = None
                cls.robot_tcp_link = False

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True  #允许重用最近已关闭的端口

class UserHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print(f'Connected: {self.client_address}')
        try:
            self.process_command()
        except Exception as e:
            print("handle:",e)
        finally:
            print(f'Closed: {self.identity}')
    #对不同的类型进行不同处理
    def process_command(self):
        #线程参数的初始化
        self.identity = None
        self.last_receive_time = datetime.datetime.now() #记录更新时间的
        self.robot_keep_live = False
        self.robot_tcp = None
        self.robot_tcp_lock_ = None
        #接收链接的身份信息
        self.request_data = self.request.recv(3000)
        self.method = self.request_data.split(b' ')[0].decode('utf-8')#获取请求的方法
        RobotLink.join(self) #进行链接者的身份判断
        if self.method == 'POST':#再接收一次，用于接收数据
            if self.request_data[-4:] == b'\r\n\r\n':
                request_data = self.request.recv(3000)
                self.request_data = self.request_data + request_data

        if self.identity == "robot":
            self.robot_process()
        elif self.identity == "cz_robot":
            self.robot_process()
        elif self.identity == "user":
            self.user_request()
        elif self.identity == "robot_video":
            self.robot_video_process()
        elif self.identity == "robot_video_red":
            self.robot_video_red_process()
        elif self.identity == "soft_video":
            self.soft_video_process()
        elif self.identity == "soft_video_red":
            self.soft_video_red_process()
        elif self.identity == "robot_speak":
            self.robot_speak_process()
        elif self.identity == "client_speak":
            self.client_speak_process()

    #本功能主要是处理机器人客户端的链接维持
    #根据心跳检测判断客户端tcp链接是否断开或者不可用
    #自动回收无效的tcp链接    
    def robot_process(self):
        while True:
            if (datetime.datetime.now() - self.last_receive_time).seconds > 15:
                try:
                    self.robot_tcp_lock_.acquire()#上锁，表示工控机的客户端链接被占用
                    try:
                        _size = struct.calcsize('I')  #获取总的包尺寸
                        res = self.request.recv(_size)
                    except Exception as e:
                        print("robot_process_1:",e)
                        res = ''

                    if len(res) != 0:
                        length, = struct.unpack('I', res)
                        if length == 0 :
                            fhead = struct.pack('I',0)
                            self.request.send(fhead) #心跳回应
                            self.last_receive_time = datetime.datetime.now()#更新时间

                    if (datetime.datetime.now() - self.last_receive_time).seconds > 35:
                        RobotLink.close_link() #删掉保存的链接
                        break
                except Exception as e:
                    print("robot_process_2:",e)
                finally:
                    self.robot_tcp_lock_.release() #释放锁
            time.sleep(5) 

    #返回bytes格式响应
    def respond_message_cerat(self, data = '', errorCode = '', msg = 'successed', successed = True):
        respond_param = {}
        respond_param["data"] = data
        respond_param["errorCode"] = errorCode
        respond_param["msg"] = msg
        respond_param["successed"] = successed
        content = b'HTTP/1.x 200 ok\r\nContent-Type: application/json\r\n\r\n' + json.dumps(respond_param).encode('utf-8')
        return content

    #处理来自后台软件的http请求
    def user_request(self):
        global socket_dict
        all_data = b''
        try:
            self.robot_tcp_lock_.acquire()#上锁，表示工控机的客户端链接被占用
            if self.robot_keep_live: #如果机器人那边链接了
                url = self.request_data.decode().split(' ')[1].replace("/cz_robot", "",1)
                if url.startswith("/gs-robot/data/device_status"):
                    back_data = self.respond_message_cerat(data = json.loads(redis_db.hget("last_status","last_status_data")))
                    self.request.sendall(back_data)
                    return
                #转发请求
                request_data = self.request_data.decode().replace("/cz_robot", "",1).encode()
                fhead = struct.pack('I',len(request_data)) 
                self.robot_tcp.request.send(fhead) 
                self.robot_tcp.request.send(request_data)
                #读取完客户端发送的心跳，读取客户端发送信息的长度
                _size = struct.calcsize('I')
                fhead = self.robot_tcp.request.recv(_size,0x100)  #0x100在c++中代表接收waitall
                self.robot_tcp.last_receive_time = datetime.datetime.now()#更新时间
                length, = struct.unpack('I', fhead)
                while length == 0:
                    fhead = self.robot_tcp.request.recv(_size,0x100)  #0x100在c++中代表接收waitall
                    length, = struct.unpack('I', fhead)
                #接收返回数据
                while True:
                    if length - len(all_data) >= 50000:
                        respond_data = self.robot_tcp.request.recv(50000) #接收来自机器人的返回数据
                    else:
                        respond_data = self.robot_tcp.request.recv(length - len(all_data)) #接收来自机器人的返回数据
                    all_data = all_data + respond_data
                    if len(all_data) >= length:
                        break
                #转发回复 
                self.request.sendall(all_data)
            else: #如果机器人没链接
                #返回错误
                back_data = self.respond_message_cerat(errorCode = "robot not link",msg = "fail", successed= False)
                self.request.sendall(back_data) 
        #异常处理
        except Exception as e:
            print("user_request:",e)
            try:
                self.robot_tcp.request.recv(50000)  #清空缓冲区
            except Exception:
                print("清空缓冲异常")
            back_data = self.respond_message_cerat(errorCode = "robot not link",msg = "fail", successed= False)
            self.request.sendall(back_data) 
        finally:
            self.robot_tcp_lock_.release() #释放锁

    #target_client_identify 收到信息要转发到的地址
    def video_message_process(self,target_client_identify):
        global socket_dict   #tcp链接存储
        while True:
            try:
                #获取要接收视频信息的长度
                _size = struct.calcsize('II')  
                fhead = self.request.recv(_size,0x100)  #0x100在c++中代表接收waitall
                if fhead != b'':
                    data_type, length= struct.unpack('II', fhead)
                elif fhead == b'': #断开链接的时候，读取数据会返回空字符串
                    break
                #心跳包
                if data_type == 24:
                    respond_fhead = struct.pack('II',24,0)
                    self.request.send(respond_fhead)
                    continue
                #按获取的长度接收信息
                if length != 0:
                    data = self.request.recv(length,0x100)  #0x100在c++中代表接收waitall
                    if target_client_identify in socket_dict.keys(): #解码端在的话才转发，否则就抛弃掉
                        socket_dict[target_client_identify].request.send(fhead)
                        socket_dict[target_client_identify].request.sendall(data)
                else:
                    if target_client_identify in socket_dict.keys():
                        socket_dict[target_client_identify].request.send(fhead)                
            except Exception as e:
                print(f"video_message_process:{target_client_identify}  ",e)
                break

    #接收机器人上传的视频，发送给后台软件
    def robot_video_process(self):
        global socket_dict   #tcp链接存储
        # 如果后台软件提前链接，解码已就位，就让机器人直接开始传输
        if "soft_video" in socket_dict.keys():
            val = struct.pack("II", 22,0)
            self.request.send(val)
        #循环接收信息并转发
        self.video_message_process("soft_video")
        del socket_dict[self.identity]  #断开连接后从链接字典中删除

    #接收机器人上传的红外视频并转发给后台软件
    def robot_video_red_process(self):
        global socket_dict   #tcp链接存储
        # 如果后台软件提前链接，解码已就位，就让机器人直接开始传输
        if "soft_video_red" in socket_dict.keys():
            val = struct.pack("II", 22,0)
            self.request.send(val)
        #循环接收信息并转发
        self.video_message_process("soft_video_red")
        del socket_dict[self.identity]  #断开连接后从链接字典中删除

    #暂时没锤子用，就转发一个开始结束信息
    def soft_video_process(self):
        global socket_dict   #tcp链接存储
        self.video_message_process("robot_video")
        del socket_dict[self.identity]  #断开连接后从链接字典中删除

    #暂时没锤子用，就转发一个开始结束信息
    def soft_video_red_process(self):
        global socket_dict   #tcp链接存储
        self.video_message_process("robot_video_red")
        del socket_dict[self.identity]  #断开连接后从链接字典中删除

    #接收音频发送给机器人
    def client_speak_process(self):
        global socket_dict   #tcp链接存储
        #循环接收信息并转发
        self.video_message_process("robot_speak")
        del socket_dict[self.identity]  #断开连接后从链接字典中删除

    #暂时没锤子用，就转发一个开始结束信息
    def robot_speak_process(self):
        global socket_dict   #tcp链接存储
        self.video_message_process("client_speak")
        del socket_dict[self.identity]  #断开连接后从链接字典中删除

if __name__ == '__main__':
    # host = socket.gethostname()
    host = "127.0.0.1"
    rt = RecviveRobotData((host, 62223)) #udp 接收上传数据的
    rn = RecviveRobotVideoNormal()
    ri = RecviveRobotVideoInfrared()
    rt.start()
    rn.start()
    ri.start()
    with ThreadedTCPServer((host, 9921), UserHandler) as server:  #自动调用close()
        print(f'robot trans server is running...')
        server.serve_forever()

