import json
from multiprocessing import Queue

PTZ_Command = {
    "ZOOM_IN" : 11, #倍率变大
    "ZOOM_OUT" : 12, #倍率变小
    "TILT_UP" : 21, #云台上仰
    "TILT_DOWN" : 22, #云台下俯
    "PAN_LEFT" : 23, #云台左转
    "PAN_RIGHT" : 24, #云台右转
    "UP_LEFT" : 25, #云台上仰和左转
    "UP_RIGHT" : 26, #云台上仰和右转
    "DOWN_LEFT" : 27, #云台下俯和左转
    "DOWN_RIGHT" : 28, #云台下俯和右转
    "PAN_AUTO" : 29, # 云台左右自动扫描
}

#有content的时候不加载字典，直接添加content后返回
def respond_message_creat(status_code=200, data='', errorCode='', msg='successed', successed=True, content=b""):
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

class Param_Init(object):
    def __init__(self):
        #临时线程变量
        self.video_process = None
        self.light_process = None
        self.trumpet_process = None
        self.robot_move_thread = None
        self.task_queue_run_thread = None
        self.speak_process = None
        #标志变量
        self.task_queue_run = False #存活状态
        self.speak_message_queue = Queue()