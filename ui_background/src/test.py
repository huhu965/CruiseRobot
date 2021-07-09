import sys
import requests
import cv2
import socket
import numpy
import time
import json
import asyncio
import websockets
import robot_api
import datetime
import json
import struct
from thread_class import *
from PyQt5.QtCore import QPoint
import redis
import os

# def exect_display():
#     cv2.namedWindow("SERVER",0);
#     cv2.resizeWindow("SERVER", 1080, 960);
#     while True:
#         response = requests.get(f"http://10.7.5.88:8080{robot_api.API['scan_map_png']}", timeout=5)
#         image_num = numpy.fromstring(response.content, numpy.uint8) #将字符串转为numpy矩阵
#         #opencv可以直接解码png二进制流
#         decimg = cv2.imdecode(image_num, cv2.IMREAD_COLOR) #将矩阵解码成图像
#         cv2.imshow('SERVER',decimg)
#     # #waitkey内的参数控制每张图像显示多少毫秒，返回值是这段时间内键盘的值
#         cv2.waitKey(10000) 
#     # response_message = json.loads(response.content)

# exect_display()


# decimg = cv2.imread('/home/huziwei/gongkong/ui_test/factory.png',cv2.IMREAD_COLOR)
# cv2.namedWindow("enhanced",0);
# cv2.resizeWindow("enhanced", 1440, 960);
# cv2.imshow("enhanced",decimg)
# cv2.waitKey(0)

# param = {"map_name":"factoryall","position_name":"1xuncha0"}
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['navigate']}", params = param, timeout=5)

# param = {"map_name":"factory","init_point_name":"End"}

# # # 添加标记点
# param = {"position_name":"7test1","type":2}
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['add_position']}", params = param, timeout=5)

# # 开始建图
# param = {"map_name":"factoryall","type":"1"}
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['start_scan_map']}", params= param,timeout=5)

# 查看存储的地图列表
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['async_stop_scan_map']}", timeout=5)

# 加载地图
# param = {"map_name":"factory"}
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['load_map']}", params = param, timeout=5)
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['delete_map']}", params = param, timeout=5)delete_map
# 转圈初始化

# param = {"map_name":"factoryall","init_point_name":"厂区入口"}
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['initialize']}", params =param, timeout=5)

# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['open_light']}", timeout=5)
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['maps']}", timeout=5)
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['open_video']}", timeout=5)
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}/gs-robot/cmd/open_video_nointer", timeout=5)
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['close_video']}", timeout=5)
response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['power_off']}", timeout=5)
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['gps_raw']}", timeout=5)
# # 查看地图的点列表

# param = {"map_name":"fsactoryall","type":2}
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['positions']}", params=param, timeout=3)

# 获取地图图片
# param = {"map_name":"test"}
# cv2.namedWindow("SERVER",0);
# cv2.resizeWindow("SERVER", 1080, 960);
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['map_png']}", params=param, timeout=20)
# image_num = numpy.fromstring(response.content, numpy.uint8) #将字符串转为numpy矩阵
# # print(response.content)
# #opencv可以直接解码png二进制流
# decimg = cv2.imdecode(image_num, cv2.IMREAD_COLOR) #将矩阵解码成图像
# cv2.imshow('SERVER',decimg)
# # #waitkey内的参数控制每张图像显示多少毫秒，返回值是这段时间内键盘的值
# cv2.waitKey()
# cv2.imwrite("test.png", decimg);
# 


# headers = {
# "Content-Type": "application/json",
# "Connection": "close",
# }
# response = requests.get(f"http://101.37.16.240:62222/gs-robot/data/device_status",headers=headers,timeout=5)
# print(response.content)


# param = {"angle": 0,
#         "gridX": 320,
#         "gridY": 180,
#         "mapName": "yinshua",
#         "name": "end7",
#         "type": 2}
# response = requests.post(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['on_map_add_position']}", # anywhere_navigate
#                         data=json.dumps(param),  #dumps直接给字典，dump要给文件指针
#                         headers=headers, timeout=3)


# param = {"destination":{"angle":0,"gridPosition":{"x":1010,"y":1005}}}

# i = 10
# while i:
#     param = {"speed":{"linearSpeed":-0.5,"angularSpeed":0}}
#     response = requests.post(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['move']}", # anywhere_navigate
#                             data=json.dumps(param),  #dumps直接给字典，dump要给文件指针
#                             headers=headers, timeout=3)

#     print(response.status_code)
#     print(response.content)
#     time.sleep(0.2)
#     i=i-1
# param = {"speed":{"linearSpeed":0,"angularSpeed":0}}
# response = requests.post(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['move']}", # anywhere_navigate
#                         data=json.dumps(param),  #dumps直接给字典，dump要给文件指针
#                         headers=headers, timeout=3)

# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['position']}", timeout=1)
# print(response.status_code)
# print(response.content)
# print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
# redis_db = redis.Redis(host='127.0.0.1', port=6379, db=0,decode_responses=True)
# key_l = redis_db.keys()
# for i in key_l:
#     redis_db.delete(i)
# key_l = redis_db.keys()
# print(key_l)
#当前文件路径
# print(os.path.realpath(__file__))
# #当前文件所在的目录，即父路径
# print(os.path.split(os.path.realpath(__file__))[0])

# a = b'hhue'
# li = list(a)
# print(li)
# print(type(li[0]))
# print(bytes(li[0:2]))

# 摄像头云台控制
# param = {"dwPTZCommand":23,"dwSpeed":1,"dwStop":0}
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['ptz_control']}", params =param, timeout=5)
# time.sleep(2)
# param = {"dwPTZCommand":23,"dwSpeed":1,"dwStop":1}
# response = requests.get(f"http://{robot_api.robot_ip}:{robot_api.robot_port}{robot_api.API['ptz_control']}", params =param, timeout=5)

# 更换服务器地址
# headers = {
# "Content-Type": "application/json",
# "Connection": "close",
# }
# response = requests.get(f"http://127.0.0.1:62223/gs-robot/cmd/change_server_ip?ip=127.0.0.1&port=62222",headers=headers,timeout=5)
print(response.status_code)
print(response.content)