import socket
import threading
import datetime
import json
import struct
import time
from play_voice import PlayVoice

# 客户端联网的基类
# 链接服务器功能
# 更新上次收到信息时间 
# 关闭链接 
# 发送心跳包给服务器 
# http响应的生成
class Client_Socket(object):
    def __init__(self,server_ip):
        self.server_ip = server_ip
        self.socket_link_flag = False #链接标志位
        self.recv_socket = None
        self.last_receive_time = datetime.datetime.now() #记录上次接收信息时间
        self.lock = threading.Lock()  #线程锁

    def connect_server(self):
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #tcp，链接服务器
        while True: #直到连接上服务器才进行下一步
            try:
                self.recv_socket.connect(self.server_ip)#尝试链接服务器
                break
            except Exception as e:
                print(e,self.server_ip)
                p = PlayVoice("链接服务器失败")
                p.start()
                time.sleep(10)
        self.socket_link_flag = True
        self.update_last_receive_time()

    #更新上次接收信息时间
    def update_last_receive_time(self):
        self.last_receive_time = datetime.datetime.now()
    #关闭链接
    def close_link(self):
        try:
            self.socket_link_flag = False
            self.recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.recv_socket.close()
            self.recv_socket = None
        except Exception as e:
            print(e)

    #有content的时候不加载字典，直接添加content后返回
    def respond_message_creat(self, status_code=200, data='', errorCode='', msg='successed', successed=True, content=b""):
        if content == b"":
            respond_param = {}
            respond_param["data"] = data
            respond_param["errorCode"] = errorCode
            respond_param["msg"] = msg
            respond_param["successed"] = successed
            respond = b'HTTP/1.x 200 ok\r\nContent-Type: application/json\r\n\r\n' + json.dumps(respond_param).encode('utf-8')
        else:
            respond = b'HTTP/1.x ' +str(status_code).encode('utf-8') +b' ok\r\nContent-Type: application/json\r\n\r\n' +content
        return respond

    #发送心跳包
    def send_heart_message(self):
        try:
            self.lock.acquire()
            fhead = struct.pack('I',0)#发送心跳包
            self.recv_socket.send(fhead)
        except Exception as e:
            print(e)
        finally:
            self.lock.release()