import time
import sys
import threading
import time
import requests
import socket
import json
import datetime
import struct
import pyaudio
from threading import Thread
from multiprocessing import Process
from gs_robot.general_function import *
#巡航任务线程
class robot_scan_mode_process(Thread):
    def __init__(self,request_process, param, robot_ip, robot_port):
        super(robot_scan_mode_process, self).__init__()
        self.request_process = request_process
        self.robot_ip = robot_ip
        self.robot_port = robot_port
        self.loop = param['loop']
        self.loop_count = param['loop_count']
        self.map_name = param['map_name']
        self.tasks = param['tasks']
        self.tasks_number = len(self.tasks) #当前队列的任务数
        self.task_running = False
        self.pause_task = False
        self.cancle_task = False
        self.now_task = {}
        self.navigate_task_error = False
        self.navigate_status = ''
    #巡查任务
    def CheckTask(self): 
        self.task_running = True
        url = f"ptz_control?dwPTZCommand={PTZ_Command['PAN_LEFT']}&dwSpeed=2&dwStop=0" # dwStop 0开始 1结束
        self.request_process.cmd_socket.sendto(url.encode('utf-8'), self.request_process.cmd_ip) #向摄像头进程发送指令
        time.sleep(4)
        url = f"ptz_control?dwPTZCommand={PTZ_Command['PAN_LEFT']}&dwSpeed=2&dwStop=1" # dwStop 0开始 1结束
        self.request_process.cmd_socket.sendto(url.encode('utf-8'), self.request_process.cmd_ip) #向摄像头进程发送指令

        time.sleep(5)

        url = f"ptz_control?dwPTZCommand={PTZ_Command['PAN_RIGHT']}&dwSpeed=2&dwStop=0" # dwStop 0开始 1结束
        self.request_process.cmd_socket.sendto(url.encode('utf-8'), self.request_process.cmd_ip) #向摄像头进程发送指令
        time.sleep(8)
        url = f"ptz_control?dwPTZCommand={PTZ_Command['PAN_RIGHT']}&dwSpeed=2&dwStop=1" # dwStop 0开始 1结束
        self.request_process.cmd_socket.sendto(url.encode('utf-8'), self.request_process.cmd_ip) #向摄像头进程发送指令

        time.sleep(5)

        url = f"ptz_control?dwPTZCommand={PTZ_Command['PAN_LEFT']}&dwSpeed=2&dwStop=0" # dwStop 0开始 1结束
        self.request_process.cmd_socket.sendto(url.encode('utf-8'), self.request_process.cmd_ip) #向摄像头进程发送指令
        time.sleep(4.5)
        url = f"ptz_control?dwPTZCommand={PTZ_Command['PAN_LEFT']}&dwSpeed=2&dwStop=1" # dwStop 0开始 1结束
        self.request_process.cmd_socket.sendto(url.encode('utf-8'), self.request_process.cmd_ip) #向摄像头进程发送指令

        time.sleep(5)
        self.task_running = False
    #暂停任务
    def tasks_pasue(self):
        self.pause_task = True
    #取消任务
    def tasks_cancle(self):
        self.cancle_task = True
    #恢复任务
    def tasks_resume(self):
        self.pause_task = False
    def navigate_status_input(self,navigate_status):
        self.navigate_status = navigate_status
    #导航指令发送
    def navigate_request_send(self, url, param=''):
        try:
            if param == '':
                response = requests.get(f"http://{self.robot_ip}:{self.robot_port}{url}", timeout=1)
            else:
                response = requests.get(f"http://{self.robot_ip}:{self.robot_port}{url}", param, timeout=1)
            response_data = json.loads(response.content)
            if not response_data['successed']:
                self.navigate_task_error = True
        except Exception:
            return False

    #开始导航指令
    def navigate_start(self,start_param):
        self.navigate_request_send('/gs-robot/cmd/position/navigate',start_param)

    #导航任务
    def NavigationTask(self,start_param): 
        self.navigate_start(start_param) #开始导航任务
        self.task_running = True
        while True:
            time.sleep(1)
            if self.cancle_task:
                self.navigate_request_send('/gs-robot/cmd/cancle_navigate')
                break
            if self.pause_task and self.task_running:
                self.navigate_request_send('/gs-robot/cmd/pause_navigate')
                self.task_running = False
            elif not self.pause_task and not self.task_running:
                self.navigate_request_send('/gs-robot/cmd/resume_navigate')
                self.task_running = True
            if self.navigate_status == "navigate_end":#退出
                self.navigate_status = ""
                break
        self.task_running = False

    #运行一次队列任务
    def run_once_tasks_queue(self):
        number = 1
        for task in self.tasks:
            if task['name'] == 'NavigationTask':
                self.NavigationTask(task["start_param"])
                self.CheckTask()
            if self.cancle_task:
                break

    def run(self):
        if self.loop:
            for i in range(self.loop_count):
                if self.cancle_task:
                    break
                self.run_once_tasks_queue()
        else:
            self.run_once_tasks_queue()
        self.request_process.task_queue_run = False
#移动线程
class robot_move_Thread(Thread): 
    def __init__(self, param):
        super(robot_move_Thread, self).__init__()
        self.param = param
        self._running = True

    def run(self): # 在启动线程后任务从这个函数里面开始执行
        count = 10
        headers = {
        "Content-Type": "application/json",
        "Connection": "close",
        }
        while count:
            try:
                if not self._running:
                    break
                response = requests.post(f"http://10.7.5.88:8080/gs-robot/cmd/move", 
                                    data=self.param,
                                    headers=headers, timeout=1)
                count = count - 1
                time.sleep(0.2)   
            except Exception:
                print("error occupy")  
                
    def end_move(self):
        self.param = json.dumps({"speed":{"linearSpeed":0,"angularSpeed":0}})
        self._running = False

    def change_direction(self,param):
        self.param = param

#查询状态更改，进行相应处理
class status_check_Thread(Thread):
    def __init__(self,main_process):
        super(status_check_Thread, self).__init__()
        self.main_process = main_process
    #判断移动线程是否执行完毕
    def move_status_check(self):
        if self.main_process.robot_move_thread != None:
            if not self.main_process.robot_move_thread.isAlive():
                self.main_process.robot_move_thread = None
    #获取导航状态
    def navigate_status_check(self):
        navigate_status = self.main_process.robot_navigate_status_update_thread.get_navigate_status()
        if navigate_status == "navigate_end":
            if self.main_process.task_queue_run:
                self.main_process.task_queue_run_thread.navigate_status_input(navigate_status) #把导航状态给到任务队列类
            self.main_process.robot_navigate_status_update_thread.init_navigate_status() #将导航状态获取队列的导航状态初始化
    #任务队列线程是否完成，完成就释放掉线程
    def task_queue_finish_check(self):
        if not self.main_process.task_queue_run and self.main_process.task_queue_run_thread != None:
            self.main_process.task_queue_run_thread == None

    def run(self): # 在启动线程后任务从这个函数里面开始执行
        while True:
            time.sleep(1)
            try:
                self.move_status_check()
                self.navigate_status_check()
                self.task_queue_finish_check()
            except Exception as e:
                continue
#提交数据线程
class robot_device_data_upload_Thread(Thread):
    def __init__(self,main_process,server_ip):
        super(robot_device_data_upload_Thread, self).__init__()
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #udp 链接服务器
        self.server_ip = server_ip
        self.main_process = main_process
        self.temperature = {}
        self.temperature["max_temperature"] = 0
        self.temperature["min_temperature"] = 0
        self.temperature["average_temperature"] = 0
        self.sensor = {}
        self.sensor['sensor1'] = 0
        self.sensor['sensor2'] = 0

        self.temperature_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.temperature_receive_socket.bind(("127.0.0.1", 8022))

        self.receive_temperature_thread = threading.Thread(target=self.recv_temperature) #接收音频信号
        self.receive_temperature_thread.daemon = True #守护线程
        self.receive_temperature_thread.start()

    def recv_temperature(self):
        while True:
            try:
                data,addr = self.temperature_receive_socket.recvfrom(512)
                data1 = data.decode('utf-8').split('&')
                self.temperature["max_temperature"] = data1[0].split('=')[1]
                self.temperature["min_temperature"] = data1[1].split('=')[1]
                self.temperature["average_temperature"] = data1[2].split('=')[1]
            except Exception as e:
                print(e)
                time.sleep(1)

    def get_max_temperature(self):
        try:
            return float(self.temperature["max_temperature"])
        except Exception as e:
            print("提交数据线程",e)
    #返回元组，有两个数据
    def get_sensor_concentration(self):
        try:
            return (float(self.sensor['sensor1']),float(self.sensor['sensor2']))
        except Exception as e:
            print("提交数据线程",e)

    def device_data_upload(self,data):#向服务器提交数据
        self.send_socket.sendto((data + '\r\n\r\n').encode("utf-8"), self.server_ip);
    
    def device_data_update(self): #从各个线程汇总相关数据
        try:
            #返回机器人状态
            device_data = self.main_process.robot_status_update_thread.get_data() #获取机器状态
            navigate_data = self.main_process.robot_navigate_status_update_thread.get_data()#获取导航状态信息
            position_data = self.main_process.robot_position_update_thread.get_data() #获取位置信息
            device_data.update(navigate_data)
            device_data.update(position_data)
            device_data.update(self.temperature)
            device_data["time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.sensor['sensor1'] = device_data['sensor1']
            self.sensor['sensor2'] = device_data['sensor2']
            self.device_data_upload(json.dumps(device_data))
        except Exception as e:
            print("提交数据线程",e)
    
    def run(self):
        while True:
            self.device_data_update()
            time.sleep(1)
#获取位置线程，初始化之后才会返回坐标，否则都是0
class robot_position_update_Thread(Thread):
    def __init__(self):
        #父类初始化
        Thread.__init__(self)
        self.robot_ip = '10.7.5.88' #机器人的内网地址
        self.robot_port = 8080
        #自己的初始化
        self.visit_data_lock = threading.Lock()

        self.robot_map_datas = {}
        self.robot_map_datas["robot_position"] = {'x':0, 'y':0,"angle":0}
        self.robot_map_datas["map_width"] = 0
        self.robot_map_datas["map_height"] = 0

    def update_data(self,data):
        try:
            positon_data = json.loads(data) #从json里恢复字典
            self.visit_data_lock.acquire()
            if "successed" not in positon_data.keys():
                self.robot_map_datas["robot_position"]["x"] = positon_data["gridPosition"]["x"]
                self.robot_map_datas["robot_position"]["y"] = positon_data["gridPosition"]["y"]
                self.robot_map_datas["robot_position"]["angle"] = positon_data["angle"]
                self.robot_map_datas["map_width"] = positon_data["mapInfo"]["gridWidth"]
                self.robot_map_datas["map_height"] = positon_data["mapInfo"]["gridHeight"]
        except Exception as e:
            print("pos", e)
        finally:
            self.visit_data_lock.release()

    #返回数据
    def get_data(self):
        try:
            return self.robot_map_datas
        except Exception:
            return False

    def run(self):
        # print(f"获取坐标 子进程{os.getpid()} 开始执行，父进程为{os.getppid()}")
        while True:
            try:
                response = requests.get(f"http://{self.robot_ip}:{self.robot_port}/gs-robot/real_time_data/position", timeout=1)
                response_message = json.loads(response.content) #从json里恢复字典
                self.update_data(response.content)
                time.sleep(2)
            except Exception as e:
                print(e)  

class SpeakProcess(Process):
    # 初始化
    def __init__(self,server_ip,message_queue_input):
        super().__init__()
        self.server_ip = server_ip
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_change_lock = threading.Lock()  #线程锁
        self.data_store_buff = []
        self.max_store_size = 32000 
        self.frameSize = 1280  # 每一帧的音频大小
        self.message_queue_input = message_queue_input

    def connect_server(self):
        while True: #直到连接上服务器才进行下一步
            try:
                self.receive_socket.connect(self.server_ip)#尝试链接服务器
                break
            except Exception as e:
                print(e,self.server_ip)
                time.sleep(10)
        
    def recv_voice_data(self):
        try:
            _size = struct.calcsize('II')
            fhead = self.receive_socket.recv(_size,0x100)  #0x100在c++中代表接收waitall
            #处理接收长度信息
            if len(fhead) == 0: #基本上是服务器端关闭了，拖着等重连启动
                return b''
            data_type, length = struct.unpack('II', fhead)
            if length == 0:
                return b''
            else:
                data = self.receive_socket.recv(length,0x100)  #接收服务器发的请求
                return data
        except Exception as e:
            print("对讲错误",e)
            return b''

    def recv_data(self):
        while True:
            buf = self.recv_voice_data()
            # 文件结束
            if not buf:
                continue
            self.stream.write(buf)

    # 收到websocket连接建立的处理
    def run(self):
        self.connect_server()
        content = b"robot_speak \r\n"
        self.receive_socket.sendall(content)#注册身份

        CHUNK = 5120#队列长度
        FORMAT = pyaudio.paInt16 #保存格式
        CHANNELS = 1  #几个通道
        RATE = 8000 #采样率，一般8000的采样率能识别出人说的话
        record_p = pyaudio.PyAudio() #实例化
        #打开获取流
        self.stream = record_p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)
        
        self.receive_data_thread = threading.Thread(target=self.recv_data) #接收音频信号
        self.receive_data_thread.daemon = True #守护线程
        self.receive_data_thread.start()

        while True:
            try:
                input_cmd = self.message_queue_input.get(False)  #非阻塞，如果空就抛异常
                if input_cmd == "process_end":
                    break
            except:
                pass
        self.receive_socket.shutdown(2)
        self.receive_socket.close()
        self.stream.stop_stream()
        self.stream.close()
        record_p.terminate()