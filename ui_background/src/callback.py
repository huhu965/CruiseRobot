from PyQt5.QtGui import QPixmap, QImage
import json
import cv2
import numpy
import os
import subprocess
import signal
import robot_api
import requests

from thread_class import message_display_Thread
class Callback(object):
#返回调用函数
#{ 响应的统一格式，successed表示请求接口是否成功，失败msg会有错误信息，如果有返回数据，统一在data里获取
#   "data"："",
#   "errorCode":"",
#   "msg":"successed",
#   "successed":"true"
# }
    def callback(self,response):
        try:
            if response.content != b"":
                response_message = json.loads(response.content) #从json里恢复字典
                if response_message["successed"] != True:
                    self.error_view_thread = message_display_Thread("error",response_message["msg"]) # 实例化自己建立的任务线程类
                    self.error_view_thread.start()
                else:
                    if response_message["data"] != "":
                        print(response_message["data"])
        except Exception as e:
            print(e)

    
    def map_png_callback(self,response):
        image_num = numpy.fromstring(response.content, numpy.uint8) #将字符串转为numpy矩阵
        #opencv可以直接解码png二进制流
        decimg = cv2.imdecode(image_num, cv2.IMREAD_COLOR) #将矩阵解码成图像
        
        shrink = cv2.cvtColor(decimg, cv2.COLOR_BGR2RGB) #将bgr(opencv)转为rgb(pyqt5)
        QtImg = QImage(shrink.data,
                                  shrink.shape[1],
                                  shrink.shape[0],
                                  shrink.shape[1] * 3,
                                  QImage.Format_RGB888)
        
        self.map_label.setPixmap(QPixmap.fromImage(QtImg))
        self.map_label.setScaledContents(True)  # 图片自适应LABEL大小
        self.map_label.show()

    def map_png_callback_location(self):
        try:
            decimg = cv2.imread('/home/huziwei/gongkong/ui_test/factoryall.png',cv2.IMREAD_COLOR)
            
            shrink = cv2.cvtColor(decimg, cv2.COLOR_BGR2RGB) #将bgr(opencv)转为rgb(pyqt5)
            QtImg = QImage(shrink.data,
                                    shrink.shape[1],
                                    shrink.shape[0],
                                    shrink.shape[1] * 3,
                                    QImage.Format_RGB888)
            #生成小车在地图上的位置
            self.map_label.setPixmap(QPixmap.fromImage(QtImg))
            self.map_label.setScaledContents(True)  # 图片自适应LABEL大小
            self.map_label.show()
        except Exception as e:
            print(e)
            return

    def video_receive_callback(self, data):
        try:
            image_num = numpy.fromstring(data, numpy.uint8) #将字符串转为numpy矩阵
            decimg = cv2.imdecode(image_num, cv2.IMREAD_COLOR) #将矩阵解码成图像
            shrink = cv2.cvtColor(decimg, cv2.COLOR_BGR2RGB) #将bgr(opencv)转为rgb(pyqt5)
            QtImg = QImage(shrink.data,
                                    shrink.shape[1],
                                    shrink.shape[0],
                                    shrink.shape[1] * 3,
                                    QImage.Format_RGB888)

            self.video_label.setPixmap(QPixmap.fromImage(QtImg))
            self.video_label.setScaledContents(True)  # 图片自适应LABEL大小
            self.video_label.show()
        except Exception:
            return

    def red_video_receive_callback(self, data):
        try:
            image_num = numpy.fromstring(data, numpy.uint8) #将字符串转为numpy矩阵
            decimg = cv2.imdecode(image_num, cv2.IMREAD_COLOR) #将矩阵解码成图像
            shrink = cv2.cvtColor(decimg, cv2.COLOR_BGR2RGB) #将bgr(opencv)转为rgb(pyqt5)
            QtImg = QImage(shrink.data,
                                    shrink.shape[1],
                                    shrink.shape[0],
                                    shrink.shape[1] * 3,
                                    QImage.Format_RGB888)

            self.red_video_label.setPixmap(QPixmap.fromImage(QtImg))
            self.red_video_label.setScaledContents(True)  # 图片自适应LABEL大小
            self.red_video_label.show()
        except Exception:
            return

    def voice_receive_callback(self, data):
        try:
            self.voice_stream.write(data)
        except Exception:
            return

    def robot_data_receive_thread_callback(self, respond):
        try:
            data = json.loads(respond.content)
            if data['successed'] != True:
                if data['errorCode'] != 'link_error':
                    self.link_status_text_label.setText("未初始化")
                else:
                    self.link_status_text_label.setText("服务器断开")
                    return
                self.battery_text_label.setText("null")
                self.robot_speed_text_label.setText("null")
                self.charger_status_text_label.setText("null")
                self.charger_status_text_label.setText("null")
                self.navigate_speed_text_label.setText("null")
            else:
                self.link_status_text_label.setText("正在运行")
                self.battery_text_label.setText(f"{data['data']['battery']}")
                self.robot_speed_text_label.setText(f"{data['data']['speed']}")
                self.navigate_speed_text_label.setText(f"{data['data']['navigationSpeedLevel']}")
                self.charger_status_text_label.setText(f"{data['data']['noticeType']}")

            self.robot_map_datas["robot_position"]["x"] = data['data']["robot_position"]["x"]
            self.robot_map_datas["robot_position"]["y"] = data['data']["robot_position"]["y"]
            self.robot_map_datas["robot_position"]["angle"] = data['data']["robot_position"]["angle"]
            self.robot_map_datas["map_width"] = data['data']["map_width"]
            self.robot_map_datas["map_height"] = data['data']["map_height"]
            x = data['data']["robot_position"]["x"]*self.map_widget.width()//self.robot_map_datas["map_width"]
            y = self.map_widget.height() - data['data']["robot_position"]["y"]*self.map_widget.height()//self.robot_map_datas["map_height"]
            self.map_label.receive_param(x,y)

            self.gas_one_text_label.setText(f"{data['data']['sensor1']}%")
            self.gas_two_text_label.setText(f"{data['data']['sensor2']}%")
            if data['data']['sensor1'] >50 or data['data']['sensor2'] >50:
                self.security_status_text_label.setText("高度风险")
                self.security_status_text_label.setStyleSheet("background-color:red;")
            elif data['data']['sensor1'] >25 or data['data']['sensor2'] >25:
                self.security_status_text_label.setText("中度风险")
                self.security_status_text_label.setStyleSheet("background-color:yellow;")
                if not self.light_is_open:
                    respond = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['open_light']}", timeout=3)
                    self.light_is_open = True
            else:
                self.security_status_text_label.setText("安全")
                self.security_status_text_label.setStyleSheet("background-color:rgb(78, 154, 6);")
                if self.light_is_open:
                    respond = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['close_light']}", timeout=3)
                    self.light_is_open = False
        except Exception as e:
            print(e)
            return

    def robot_position_callback(self,data):  #实时显示机器人位置
        try:
            self.robot_map_datas["robot_position"]["x"] = data["gridPosition"]["x"]
            self.robot_map_datas["robot_position"]["y"] = data["gridPosition"]["y"]
            self.robot_map_datas["robot_position"]["angle"] = data["angle"]
            self.robot_map_datas["map_width"] = data["mapInfo"]["gridWidth"]
            self.robot_map_datas["map_height"] = data["mapInfo"]["gridHeight"]
            x = data["gridPosition"]["x"]*self.map_widget.width()//self.robot_map_datas["map_width"]
            y = self.map_widget.height() - data["gridPosition"]["y"]*self.map_widget.height()//self.robot_map_datas["map_height"]
            self.map_label.receive_param(x,y)
        except Exception:
            return

    def video_open_callback(self,data = ''): #启动视频解码
        try:
            if self.video_process == None:
                self.video_process = subprocess.Popen("./src/video_decode")#启动解码程序
        except Exception as e:
            print(e)
    
    def video_close_callback(self,data = ''): #关闭视频解码
        try:
            if self.video_process != None:
                self.video_process.send_signal(signal.SIGINT)
        except Exception as e:
            print(e)
        self.video_process = None #解码进程关闭
        self.video_red_process = None #解码进程关闭