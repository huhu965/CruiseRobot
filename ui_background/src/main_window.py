import sys
import requests
import cv2
import numpy
import socket
import os
import subprocess
import signal
import pyaudio

from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.Qt import *
from PyQt5.QtCore import QTimer


import handle
from Ui_display import Ui_MainWindow
from thread_class import *
from callback import Callback
from position_dialog import add_position_Dialog
class MyMainWindow(QMainWindow, Ui_MainWindow, Callback):
    def __init__(self, parent=None):
        super(MyMainWindow,self).__init__(parent)
        self.setupUi(self)
        ####这块要存一个json文件，每次都直接加载就好了，后期修改
        with open("robot_map_datas.json","r") as file:
            self.robot_map_datas = json.load(file)
        with open("task_queue.json","r") as file:
   
            self.navigete_task_queue = json.load(file)
            
        self.max_map = False
        self.max_video = False
        self.initialize_robot_finish = False
        self.map_set_navigate = False #地图设置导航点标志位
        self.map_add_position = False #地图虚空标点标志位
        self.ptz_display_flag = False #云台界面是否显示
        self.robot_display_flag = False #云台界面是否显示
        self.isDoubleClick = False #判断单双击
        self.video_process = None #解码进程
        self.light_is_open = False
        self.temprory_thread_list = [] #按键之类短线程放在这里面，定时清理已经执行完成的

        self.video_open_callback()
        self.init_software()
    
    
    def init_software(self):
        #地图
        self.new_map_act.triggered.connect(lambda: handle.handle_new_map(self))
        self.extend_map_act.triggered.connect(lambda: handle.handle_extend_map(self))
        self.load_map_act.triggered.connect(lambda: handle.handle_load_map(self))
        self.delete_map_act.triggered.connect(lambda: handle.handle_delete_map(self))
        #标记点
        self.add_position_act.triggered.connect(lambda: handle.handle_add_position(self))
        self.delete_position_act.triggered.connect(lambda: handle.handle_delete_position(self))
        #导航
        self.start_navigate_act.triggered.connect(lambda: handle.handle_start_navigate(self))
        self.pause_navigate_act.triggered.connect(lambda: handle.handle_pause_navigate(self))
        self.resume_navigate_act.triggered.connect(lambda: handle.handle_resume_navigate(self))
        self.cancel_navigate_act.triggered.connect(lambda: handle.handle_cancel_navigate(self))
        #速度设置
        self.low_speed_act.triggered.connect(lambda: handle.handle_low_speed(self))
        self.middle_speed_act.triggered.connect(lambda: handle.handle_middle_speed(self))
        self.high_speed_act.triggered.connect(lambda: handle.handle_high_speed(self))
        #左边四个按键
        self.left_up_Button.clicked.connect(lambda: handle.handle_left_up(self))
        self.left_down_Button.clicked.connect(lambda: handle.handle_left_down(self))
        self.left_right_Button.clicked.connect(lambda: handle.handle_left_right(self))
        self.left_left_Button.clicked.connect(lambda: handle.handle_left_left(self))
        #右边四个按键
        self.right_up_Button.clicked.connect(lambda: handle.handle_right_up(self))
        self.right_down_Button.clicked.connect(lambda: handle.handle_right_down(self))
        self.right_right_Button.clicked.connect(lambda: handle.handle_right_right(self))
        self.right_left_Button.clicked.connect(lambda: handle.handle_right_left(self))

        self.PTZ_control_Button.clicked.connect(lambda: handle.handle_PTZ_control(self))
        self.navigate_back_Button.clicked.connect(lambda: handle.handle_navigate_back(self))
        self.navigate_cruise_Button.clicked.connect(lambda: handle.handle_task_cruise(self))
        self.navigate_stop_Button.clicked.connect(lambda: handle.handle_task_stop(self))

        self.add_navigate_task_Button.clicked.connect(lambda: handle.handle_add_navigate_task(self))
        self.delect_task_point_Button.clicked.connect(lambda: handle.handle_delect_task_point(self))
        self.resume_navigate_task_Button.clicked.connect(lambda: handle.handle_task_resume(self))
        self.Robot_control_Button.clicked.connect(lambda: handle.handle_Robot_control(self))

        self.task_tabview_display() #更新任务信息

        #视频接收线程sp
        self.video_receive_thread = message_receive_Thread('127.0.0.1', 8000) # 实例化自己建立的任务线程类
        self.video_receive_thread.signal.connect(self.video_receive_callback) #设置任务线程发射信号触发的函数
        self.video_receive_thread.start()

        #视频接收线程
        self.red_video_receive_thread = message_receive_Thread('127.0.0.1', 8003) # 实例化自己建立的任务线程类
        self.red_video_receive_thread.signal.connect(self.red_video_receive_callback) #设置任务线程发射信号触发的函数
        self.red_video_receive_thread.start()

        #声音接收线程
        CHUNK = 5120 #一帧的数据量
        FORMAT = pyaudio.paInt16 #保存格式
        CHANNELS = 1  #几个通道
        RATE = 8000 #采样率，一般8000的采样率能识别出人说的话

        self.receive_p = pyaudio.PyAudio()
        self.voice_stream = self.receive_p.open(format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True,
        frames_per_buffer=CHUNK)

        self.voice_receive_thread = message_receive_Thread('127.0.0.1', 8001) # 实例化自己建立的任务线程类
        self.voice_receive_thread.signal.connect(self.voice_receive_callback) #设置任务线程发射信号触发的函数
        self.voice_receive_thread.start()

        # #数据接收线程  ---改为长链接
        request_param = creat_request_param("Get", "device_status",loop=True)
        self.robot_right_thread = http_request_Thread(request_param) # 实例化自己建立的任务线程类
        self.robot_data_receive_thread = http_request_Thread(request_param,wait_timeout = 4 , time_interval = 2) # 实例化自己建立的任务线程类 
        self.robot_data_receive_thread.signal.connect(self.robot_data_receive_thread_callback) #设置任务线程发射信号触发的函数
        self.robot_data_receive_thread.start()

        # self.robot_pos_thread = robot_current_position_Thread()
        # self.robot_pos_thread.signal.connect(self.robot_position_callback)
        # self.robot_pos_thread.start()
        
        self.robot_button_widget.hide()#按键隐藏
        self.ptz_button_widget.hide()
        self.map_png_callback_location()#直接本地读图片

    def task_tabview_display(self):
        param_dict = {"1xuncha0":"1区巡查点1","1beng":"1区泵房",
                    "1xuncha2":"1区巡查点2","7beng":"7区泵房",
                    "7ruanguan1":"7区软管区","7navi1":"7区巡查点1",
                    "7navi2":"7区巡查点2","1xuncha3":"1区巡查点3",
                    "厂区出口":"厂区出口"}
        model = QStandardItemModel(10, 2)
        model.setHorizontalHeaderLabels(['类型','任务点'])
        task_queue = self.navigete_task_queue['tasks']
        for row in range(len(task_queue)):
            if task_queue[row]["name"] == "NavigationTask":
                item = QStandardItem('导航任务')
            else:
                item = QStandardItem('其他')
            model.setItem(row, 0, item)

            item = QStandardItem( param_dict[str(task_queue[row]["start_param"]['position_name'])] )
            model.setItem(row, 1, item)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setModel(model)

    def arrange_widget(self):
        if not self.max_map and not self.max_video:
            self.map_widget.setGeometry(5, 5, self.centralwidget.width()/4*2,self.centralwidget.height()/8*6)

            self.video_widget.setGeometry(self.map_widget.width()+10, 5, 
                                            self.centralwidget.width()/10*3, #宽
                                            self.centralwidget.height()/8*3-3)#高

            self.red_video_widget.setGeometry(self.map_widget.width()+10, 
                                            self.video_widget.height()+7, 
                                            self.centralwidget.width()/10*3,
                                            self.centralwidget.height()/8*3)

            self.robot_control_widget.setGeometry(5, self.map_widget.height()+10, 
                                            self.centralwidget.width()/5*4, #宽
                                            self.centralwidget.height()/16*3)

            self.robot_status_widget.setGeometry(self.video_widget.pos().x() + self.video_widget.width()+5,
                                            20, 
                                            self.centralwidget.width()/12*2,
                                            self.centralwidget.height()/8*2)

            self.sensor_data_widget.setGeometry(self.robot_status_widget.pos().x(), 
                                                30 + self.robot_status_widget.height(),
                                                self.centralwidget.width()/12*2,
                                                self.centralwidget.height()/8*1)
                                                
            self.ptz_button_widget.setGeometry(self.robot_control_widget.width()+ 10, 
                                                self.map_widget.height()+10,
                                                self.centralwidget.width()/12*2,
                                                self.centralwidget.height()/32*3)
            
            self.robot_button_widget.setGeometry(self.robot_control_widget.width()+ 10, 
                                                self.map_widget.height()+ self.ptz_button_widget.height() + 15,
                                                self.centralwidget.width()/12*2,
                                                self.centralwidget.height()/32*3)

            self.tableView.setGeometry(self.robot_status_widget.pos().x(), 
                                                40 + self.robot_status_widget.height() + self.sensor_data_widget.height(),
                                                self.centralwidget.width()/12*2,
                                                self.centralwidget.height()/8*2)
        elif self.max_map:
            self.map_widget.setGeometry(0, 0, self.centralwidget.width(),self.centralwidget.height())
        elif self.max_video:
            self.video_widget.setGeometry(0, 0, self.centralwidget.width(),self.centralwidget.height()) 

    def resizeEvent(self,event):#修正界面视图
        self.arrange_widget()

    def mouseDoubleClickEvent(self, event):
        center_pos = self.centralwidget.mapFromParent(event.pos())
        if event.buttons () == Qt.LeftButton:#左键双击放大缩小
            self.isDoubleClick = True #用于屏蔽左键单击
            if self.video_widget.geometry().contains(center_pos) and not self.max_map:#geometry可以获取控件的整体位置，用是否包含按键位置就能判断是否在该控件上
                if not self.max_video:
                    self.max_video = not self.max_video
                    self.map_widget.hide()
                    self.video_widget.setGeometry(0, 0, self.centralwidget.width(),self.centralwidget.height())
                    self.video_widget.raise_()#放置在最上层
                else:
                    self.max_video = not self.max_video
                    self.arrange_widget()
                    self.map_widget.show()

            elif self.map_widget.geometry().contains(center_pos):#geometry可以获取控件的整体位置，用是否包含按键位置就能判断是否在该控件上
                if not self.max_map:
                    self.max_map = not self.max_map
                    self.map_widget.setGeometry(0, 0, self.centralwidget.width(),self.centralwidget.height())
                    self.map_widget.raise_()#放置在最上层
                else:
                    self.max_map = not self.max_map
                    self.arrange_widget()

    def mousePressEvent(self, event):
        center_pos = self.centralwidget.mapFromParent(event.pos())#evnet.pos()获取的是mainwindow的坐标，要转为centerwidget坐标才能用
        if event.buttons () == Qt.LeftButton:#左键才能设置坐标
            QTimer.singleShot(200, lambda: self.judgeClick(event,center_pos))

    def judgeClick(self, event,center_pos):
        if self.isDoubleClick:
            self.isDoubleClick = False
        else:
            if self.map_widget.geometry().contains(center_pos): #contains要用父控件的坐标来判断在不在里面，如果不是父控件，坐标是有问题的
                if self.map_set_navigate or self.map_add_position:
                    map_pos = self.map_widget.mapFromParent(center_pos)
                    # self.map_label.receive_param(map_pos.x(),map_pos.y())####用来画小车轨迹                                  
                    x = map_pos.x()*self.robot_map_datas["map_width"]//self.map_widget.width()
                    y = self.robot_map_datas["map_height"] - map_pos.y()*self.robot_map_datas["map_height"]//self.map_widget.height()
                    print(x,y)
                    # angle = handle.handle_map_setting(self)
                    # if angle == "error":
                    #     return
                    # if self.map_set_navigate:
                    #     param = {"destination":{"angle":angle,
                    #                             "gridPosition":{"x":x,"y":y}}}
                    #     request_param = creat_request_param("Post", "anywhere_navigate",param)
                    #     self.map_set_navigate_thread = http_request_Thread(request_param)
                    #     self.map_set_navigate_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
                    #     self.map_set_navigate_thread.start()
                    # elif self.map_add_position:
                    #     dialog = add_position_Dialog()
                    #     p = self.centralwidget.mapToGlobal(QPoint(50,50)) #将相对坐标转为绝对坐标
                    #     dialog.setGeometry(p.x(),p.y(), 100,100)
                    #     result = dialog.exec_()
                    #     if result == dialog.Accepted:
                    #         param_position = dialog.get_param_map_add()
                    #         param = {"angle": angle,
                    #                 "gridX": x,
                    #                 "gridY": y,
                    #                 "mapName": self.robot_map_datas["map_name"],
                    #                 "name": param_position["name"],
                    #                 "type": 2}
                    #         # print(json.dumps(param))
                    #         request_param = creat_request_param("Post", "on_map_add_position",param)
                    #         self.map_add_position_thread = http_request_Thread(request_param)
                    #         self.map_add_position_thread.signal.connect(self.callback) #设置任务线程发射信号触发的函数
                    #         self.map_add_position_thread.start()

    def contextMenuEvent(self, event):#右键功能
        center_pos = self.centralwidget.mapFromParent(event.pos())
        if not self.video_widget.geometry().contains(center_pos) and not self.map_widget.geometry().contains(center_pos):
            cmenu = QMenu(self)

            openAct = cmenu.addAction("刷新视频")
            #使用exec_()方法显示菜单。从鼠标右键事件对象中获得当前坐标。mapToGlobal()方法
            #把当前组件的相对坐标转换为窗口（window）的绝对坐标
            action = cmenu.exec_(self.mapToGlobal(event.pos())) 
                
            if action == openAct:         #打开
                request_params = []
                request_param = creat_request_param("Get", "close_video")
                request_params.append(request_param)
                request_param = creat_request_param("Get", "open_video")
                request_params.append(request_param)
                self.video_refush_thread = http_request_Thread(request_params,time_interval = 4)
                self.video_refush_thread.start()

        #设置导航点     
        elif self.map_widget.geometry().contains(center_pos):
            cmenu = QMenu(self)
            openAct = cmenu.addAction("地图设置导航点")
            add_positonAct = cmenu.addAction("地图添加导航点")
            closeAct = cmenu.addAction("关闭地图设置")
            action = cmenu.exec_(self.mapToGlobal(event.pos())) 
            if action == openAct:         #打开
                if self.map_add_position:
                    self.map_add_position = False
                self.map_set_navigate = True
                self.map_widget.setCursor(Qt.UpArrowCursor)
                    # pixmap = QPixmap('Cursor_png/01.png')
                    # #2. 将光标对象传入鼠标对象中
                    # cursor = QCursor(pixmap)

            elif action == closeAct:         #隐藏
                self.map_set_navigate = False
                self.map_widget.setCursor(Qt.ArrowCursor)

            elif action == add_positonAct:         #添加点
                self.map_add_position = True
                if self.map_set_navigate:
                    self.map_set_navigate = False
                self.map_add_position = True
                self.map_widget.setCursor(Qt.CrossCursor)
            

    def closeEvent(self, event):#关闭窗口的时候可以执行一些需要关闭的指令
        self.video_close_callback()
        self.voice_stream.stop_stream()
        self.voice_stream.close()
        self.receive_p.terminate()
        with open("robot_map_datas.json","w+") as file: #将数据写入json文件中，用于存储一些数据
            json.dump(self.robot_map_datas,file, indent=4)
        with open("task_queue.json", "w+") as file:
            json.dump(self.navigete_task_queue,file, indent=4)
        event.accept()  #关闭窗口


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_()) #退出