from gs_robot.general_function import respond_message_creat
from gs_robot.robot_thread_class import *

def data_test(self,param = ""):
    self.exam_cmd_queue.put("开始考核")
    back_data = self.respond_message_creat()
    return back_data