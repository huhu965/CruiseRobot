from map_dialog import *
from position_dialog import *
from navigate_dialog import *
from thread_class import *
from PyQt5.QtCore import QPoint
import time
from robot_api import PTZ_Command


# def creat_new_thread(self,request_params,wait_timeout = 5 , time_interval = 0):
#     new_thread = http_request_Thread(request_params, wait_timeout , time_interval) # 实例化自己建立的任务线程类
#     new_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
#     new_thread.start()
#     return new_thread   #  返回的对象指针

def handle_map_setting(self):
    dialog = get_angle_Dialog()
    p = self.centralwidget.mapToGlobal(QPoint(50,50)) #将相对坐标转为绝对坐标
    dialog.setGeometry(p.x(),p.y(), 100,100)
    result = dialog.exec_()
    if result == dialog.Accepted:
        param = dialog.get_param()
        #获取到的是整数,如果报错就返回的是 “error”
        return param
    else:
        return "error"

#####地图相关处理函数
def handle_new_map(self):
    dialog = new_map_Dialog()
    # dialog.setGeometry(0, 0, 351,321)
    # print(self.centralwidget.mapToGlobal(QPoint(50,50)))
    #mapFromGlobal #将绝对坐标转为控件的相对坐标
    #pos()可以获取相对父类的坐标
    p = self.centralwidget.mapToGlobal(QPoint(50,50)) #将相对坐标转为绝对坐标
    dialog.setGeometry(p.x(),p.y(), 100,100)
    result = dialog.exec_()
    if result == dialog.Accepted:
        param = dialog.get_param()
        request_param = creat_request_param("Get", "start_scan_map",param)
        self.new_map_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
        self.new_map_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
        self.new_map_thread.start()

def handle_extend_map(self):
    dialog = extend_map_Dialog()
    p = self.centralwidget.mapToGlobal(QPoint(50,50)) #将相对坐标转为绝对坐标
    dialog.setGeometry(p.x(),p.y(), 100,100)
    result = dialog.exec_()
    if result == dialog.Accepted:
        param = dialog.get_param()
        request_param = creat_request_param("Get", "start_scan_map",param)
        self.extend_map_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
        self.extend_map_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
        self.extend_map_thread.start()

def handle_load_map(self):
    dialog = load_map_Dialog()  
    p = self.centralwidget.mapToGlobal(QPoint(50,50)) #将相对坐标转为绝对坐标
    dialog.setGeometry(p.x(),p.y(), 100,100)
    result = dialog.exec_()          
    if result == dialog.Accepted:
        param = dialog.get_param()
        request_param = creat_request_param("Get", "map_name",param)
        self.load_map_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
        self.load_map_thread.signal.connect(self.map_png_callback) #设置任务线程发射信号触发的函数
        self.load_map_thread.start()
        


def handle_delete_map(self):
    dialog = delete_map_Dialog()
    p = self.centralwidget.mapToGlobal(QPoint(50,50)) #将相对坐标转为绝对坐标
    dialog.setGeometry(p.x(),p.y(), 100,100)
    result = dialog.exec_()
    if result == dialog.Accepted:
        param = dialog.get_param()
        request_param = creat_request_param("Get", "delete_map",param)
        self.delete_map_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
        self.delete_map_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
        self.delete_map_thread.start()

#####标记点相关处理函数
def handle_add_position(self):
    dialog = add_position_Dialog()
    p = self.centralwidget.mapToGlobal(QPoint(50,50)) #将相对坐标转为绝对坐标
    dialog.setGeometry(p.x(),p.y(), 100,100)
    result = dialog.exec_()
    if result == dialog.Accepted:
        param = dialog.get_param()
        request_param = creat_request_param("Get", "add_positions",param)
        self.add_positions_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
        self.add_positions_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
        self.add_positions_thread.start()

def handle_delete_position(self):
    dialog = delete_position_Dialog()
    p = self.centralwidget.mapToGlobal(QPoint(50,50)) #将相对坐标转为绝对坐标
    dialog.setGeometry(p.x(),p.y(), 100,100)
    result = dialog.exec_()
    if result == dialog.Accepted:
        param = dialog.get_param()
        request_param = creat_request_param("Get", "delete_positions",param)
        self.delete_positions_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
        self.delete_positions_thread.signal.connect(self.load_map_callback) #设置任务线程发射信号触发的函数
        self.delete_positions_thread.start()

#####导航相关处理函数
def handle_start_navigate(self):
    dialog = start_navigate_Dialog()
    p = self.centralwidget.mapToGlobal(QPoint(50,50)) #将相对坐标转为绝对坐标
    dialog.setGeometry(p.x(),p.y(), 100,100)
    result = dialog.exec_()
    if result == dialog.Accepted:
        param = dialog.get_param()
        request_param = creat_request_param("Get", "navigate",param)
        self.start_navigate_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
        self.start_navigate_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
        self.start_navigate_thread.start()

def handle_pause_navigate(self):
    request_param = creat_request_param("Get", "pause_navigate")
    self.pause_navigate_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.pause_navigate_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.pause_navigate_thread.start()

def handle_resume_navigate(self):
    request_param = creat_request_param("Get", "resume_navigate")
    self.resume_navigate_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.resume_navigate_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.resume_navigate_thread.start()

def handle_cancel_navigate(self):
    request_param = creat_request_param("Get", "cancel_navigate")
    self.cancel_navigate_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.cancel_navigate_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.cancel_navigate_thread.start()

#####速度设置
def handle_low_speed(self):
    param = {"level":0}
    request_param = creat_request_param("Get", "set_speed_level",param)
    self.set_speed_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.set_speed_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.set_speed_thread.start()

def handle_middle_speed(self):
    param = {"level":1}
    request_param = creat_request_param("Get", "set_speed_level",param)
    self.set_speed_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.set_speed_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.set_speed_thread.start()

def handle_high_speed(self):
    param = {"level":2}
    request_param = creat_request_param("Get", "set_speed_level",param)
    self.set_speed_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.set_speed_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.set_speed_thread.start()

def handle_left_up(self):
    request_params = []
    param = {"dwPTZCommand":PTZ_Command["TILT_UP"],"dwSpeed":1,"dwStop":0}
    request_param = creat_request_param("Get", "ptz_control",param)
    request_params.append(request_param)
    param = {"dwPTZCommand":PTZ_Command["TILT_UP"],"dwSpeed":1,"dwStop":1}
    request_param = creat_request_param("Get", "ptz_control",param)
    request_params.append(request_param)
    
    self.ptz_control_thread = http_request_Thread(request_params,time_interval=2) # 实例化自己建立的任务线程类
    self.ptz_control_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.ptz_control_thread.start()

def handle_left_down(self):
    request_params = []
    param = {"dwPTZCommand":PTZ_Command["TILT_DOWN"],"dwSpeed":1,"dwStop":0}
    request_param = creat_request_param("Get", "ptz_control",param)
    request_params.append(request_param)
    param = {"dwPTZCommand":PTZ_Command["TILT_DOWN"],"dwSpeed":1,"dwStop":1}
    request_param = creat_request_param("Get", "ptz_control",param)
    request_params.append(request_param)
    
    self.ptz_control_thread = http_request_Thread(request_params,time_interval=2) # 实例化自己建立的任务线程类
    self.ptz_control_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.ptz_control_thread.start()

def handle_left_left(self):
    request_params = []
    param = {"dwPTZCommand":PTZ_Command["PAN_LEFT"],"dwSpeed":1,"dwStop":0}
    request_param = creat_request_param("Get", "ptz_control",param)
    request_params.append(request_param)
    param = {"dwPTZCommand":PTZ_Command["PAN_LEFT"],"dwSpeed":1,"dwStop":1}
    request_param = creat_request_param("Get", "ptz_control",param)
    request_params.append(request_param)
    print(request_params)
    
    self.ptz_control_thread = http_request_Thread(request_params,time_interval=2) # 实例化自己建立的任务线程类
    self.ptz_control_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.ptz_control_thread.start()

def handle_left_right(self):
    request_params = []
    param = {"dwPTZCommand":PTZ_Command["PAN_RIGHT"],"dwSpeed":1,"dwStop":0}
    request_param = creat_request_param("Get", "ptz_control",param)
    request_params.append(request_param)
    param = {"dwPTZCommand":PTZ_Command["PAN_RIGHT"],"dwSpeed":1,"dwStop":1}
    request_param = creat_request_param("Get", "ptz_control",param)
    request_params.append(request_param)
    
    self.ptz_control_thread = http_request_Thread(request_params,time_interval=2) # 实例化自己建立的任务线程类
    self.ptz_control_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.ptz_control_thread.start()

#机器人控制按键响应
def handle_Robot_control(self):
    if not self.robot_display_flag:
        self.robot_button_widget.show()
        self.robot_display_flag = True
    else:
        self.robot_button_widget.hide()
        self.robot_display_flag = False  

def handle_add_navigate_task(self):
    try:
        dialog = add_navigate_task_Dialog()
        p = self.centralwidget.mapToGlobal(QPoint(50,50)) #将相对坐标转为绝对坐标
        dialog.setGeometry(p.x(),p.y(), 100,100)
        result = dialog.exec_()
        if result == dialog.Accepted:
            param = dialog.get_param()
            task_param = {"name":"NavigationTask"}
            task_param["start_param"] = {}
            task_param["start_param"]["map_name"] = self.robot_map_datas["map_name"]
            task_param["start_param"]["position_name"] = param["position_name"]
        if param['number'] == 0 or param['number'] > len(self.navigete_task_queue['tasks']):
            self.navigete_task_queue['tasks'].append(task_param)
        else:
            self.navigete_task_queue['tasks'].insert(param['number']-1,task_param)
        self.task_tabview_display()
    except Exception:
        return

def handle_delect_task_point (self):
    try:
        dialog = delect_task_point_Dialog()
        p = self.centralwidget.mapToGlobal(QPoint(50,50)) #将相对坐标转为绝对坐标
        dialog.setGeometry(p.x(),p.y(), 100,100)
        result = dialog.exec_()
        if result == dialog.Accepted:
            param = dialog.get_param()
        if param['number'] == 0:
            del self.navigete_task_queue['tasks'][0]
        elif param['number'] > len(self.navigete_task_queue['tasks']):
            del self.navigete_task_queue['tasks'][-1]
        else:
            del self.navigete_task_queue['tasks'][param['number']-1]
        
        self.task_tabview_display()
    except Exception:
        return

#云台控制按键显示
def handle_PTZ_control(self):
    if not self.ptz_display_flag:
        self.ptz_button_widget.show()
        self.ptz_display_flag = True
    else:
        self.ptz_button_widget.hide()
        self.ptz_display_flag = False 

def handle_navigate_back(self):
    #取消队列任务，导航回原点
    request_params = []
    request_param = creat_request_param("Get", "cancle_task_queue")
    request_params.append(request_param)
    param = {"map_name":"factoryall","position_name":"厂区出口"}
    request_param = creat_request_param("Get", "navigate",param)
    request_params.append(request_param)

    self.cancle_scan_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.cancle_scan_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.cancle_scan_thread.start()

def handle_task_cruise(self):
    request_param = creat_request_param("Post", "start_task_queue", self.navigete_task_queue)
    self.robot_scan_mode_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.robot_scan_mode_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.robot_scan_mode_thread.start()

def handle_task_stop(self):
    request_param = creat_request_param("Get", "stop_task_queue")
    self.stop_scan_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.stop_scan_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.stop_scan_thread.start()

def handle_task_resume(self):
    request_param = creat_request_param("Get", "resume_task_queue")
    self.resume_scan_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.resume_scan_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.resume_scan_thread.start()

#控制小车
def handle_right_up(self):
    param = {"speed":{"linearSpeed":0.3,"angularSpeed":0}}
    request_param = creat_request_param("Post", "move",param)
    self.robot_advance_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.robot_advance_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.robot_advance_thread.start()

def handle_right_down(self):
    param = {"speed":{"linearSpeed":-0.3,"angularSpeed":0}}
    request_param = creat_request_param("Post", "move",param)
    self.robot_back_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.robot_back_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.robot_back_thread.start()

def handle_right_left(self):
    param = {"speed":{"linearSpeed":0.3,"angularSpeed":0.2}}
    request_param = creat_request_param("Post", "move",param)
    self.robot_left_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.robot_left_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.robot_left_thread.start()

def handle_right_right(self):
    param = {"speed":{"linearSpeed":0.3,"angularSpeed":-0.2}}
    request_param = creat_request_param("Post", "move",param)
    self.robot_right_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
    self.robot_right_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
    self.robot_right_thread.start()

