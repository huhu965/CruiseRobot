from gs_robot.general_function import respond_message_creat
from gs_robot.robot_thread_class import *
import sys
import os
import subprocess
import signal
import requests

def position_navigate(self, param = ""):
    response = requests.get(f"http://{self.robot_ip}:{self.robot_port}/gs-robot/cmd/position/navigate",params=param, timeout=1)
    back_data = respond_message_creat(content=response.content)
    return back_data
    
def move(self, post_data):
    try:
        if self.robot_move_thread == None:
            self.robot_move_thread = robot_move_Thread(post_data)
            self.robot_move_thread.start()
        # else:
        #     self.robot_move_thread.change_direction(post_data)
        back_data = respond_message_creat()
    except Exception as e:
        back_data = respond_message_creat(msg = f"move error:{e}")
    finally:
        return back_data
      
#打开视频传输
def open_video(self, param = "", robot_usr = False):
    # voice_source_path = os.path.split(os.path.realpath(__file__))[0]
    try:
        if self.video_process == None:
            self.video_process = subprocess.Popen("./video_trans")#启动解码程序
    except Exception as e:
        print(e)
    if not robot_usr:
        back_data = respond_message_creat()
        return back_data
#关闭视频传输
def close_video(self, param = "", robot_usr = False):
    try:
        if self.video_process != None:
            self.video_process.send_signal(signal.SIGINT)
    except Exception as e:
        print(e)
    self.video_process = None
    if not robot_usr:
        back_data = respond_message_creat()
        return back_data

#处理云台控制指令
def ptz_control(self,  param = ""):
    print(param)
    self.cmd_socket.sendto(("ptz_control?" + param).encode('utf-8'), self.cmd_ip) #向摄像头进程发送指令
    back_data = self.respond_message_creat()
    return back_data

def start_task_queue(self,post_data):
    try:
        param = json.loads(post_data) #生成字典
        if not self.task_queue_run:
            self.task_queue_run = True
            self.task_queue_run_thread = robot_scan_mode_process(self, param,"10.7.5.88",8080)
            self.task_queue_run_thread.start()
            back_data = respond_message_creat()
        else:
            back_data = respond_message_creat(data="task_queue_running")
    except Exception as e:
        back_data = respond_message_creat(msg = f"start task queue error:{e}")
    finally:
        return back_data

#处理暂停导航任务队列
def stop_task_queue(self, param = ""):
    try:
        if self.task_queue_run:
            self.task_queue_run_thread.tasks_pasue()
        back_data = self.respond_message_creat()
    except Exception as e:
        back_data = respond_message_creat(msg = f"stop task queue error:{e}")
    finally:
        return back_data

#处理恢复导航任务队列
def resume_task_queue(self, param = ""):
    try:
        if self.task_queue_run:
            self.task_queue_run_thread.tasks_resume()
        back_data = respond_message_creat()
    except Exception as e:
        back_data = respond_message_creat(msg = f"resume task queue error{e}")
    finally:
        return back_data
#处理取消导航任务队列
def cancle_task_queue(self, param = ""):
    try:
        if self.task_queue_run:
            self.task_queue_run_thread.tasks_cancle()
        back_data = respond_message_creat()
    except Exception as e:
        back_data = respond_message_creat(msg = f"cancle task queue error:{e}")
    finally:
        return back_data
def power_off(self, param = ""):
    back_data = respond_message_creat()
    os.system('poweroff')
    return back_data


# def handle_open_light(self):
#     try:
#         back_data = self.respond_message_creat()
#         self.light_process = subprocess.Popen("/home/os/testgpio -p 2 -s 1",shell=True)#启动解码程序
#     except:
#         back_data = self.respond_message_creat(msg = "light error")
#     finally:
#         return back_data

# def handle_close_light(self):
#     try:
#         back_data = self.respond_message_creat()
#         self.light_process = subprocess.Popen("/home/os/testgpio -p 2 -s 0",shell=True)#启动解码程序
#     except:
#         back_data = self.respond_message_creat(msg = "light error")
#     finally:
#         return back_data
 

# def handle_open_trumpet(self):
#     try:
#         back_data = self.respond_message_creat()
#         self.trumpet_process = subprocess.Popen("/home/os/testgpio -p 4 -s 1",shell=True)#启动解码程序
#     except:
#         back_data = self.respond_message_creat(msg = "trumpet error")
#     finally:
#         return back_data


# def handle_close_trumpet(self):
#     try:
#         back_data = self.respond_message_creat()
#         self.trumpet_process = subprocess.Popen("/home/os/testgpio -p 4 -s 0",shell=True)#启动解码程序
#     except:
#         back_data = self.respond_message_creat(msg = "trumpet error")
#     finally:
#         return back_data