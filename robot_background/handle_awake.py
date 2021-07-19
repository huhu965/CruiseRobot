import socket
import os
import sys
import threading
import time
import datetime
import json
from threading import Thread
from multiprocessing import Process, Queue
from play_voice import PlayVoice
import random
from audio_recognize import AudioRecognizeWebsocket ,speech_recognition_Process

class BaseVoicePlay(object):
    def __init__(self):
        with open("question_param.json","r") as file: #读入题目
            self.voice_name_dict = json.load(file)
        self.voice_source_path = "./voice_source/"

    #播放问题的音频  
    def play_question_audio(self,question_lib_name,number):
        self.question_play_handle = PlayVoice(self.voice_source_path + self.voice_name_dict[question_lib_name][number]["file_name"])
        self.question_play_handle.start()
        self.question_play_handle.join()#等待音频播放完
    #播放系统声音
    def play_system_audio(self, name):
        self.system_play_handle = PlayVoice(self.voice_source_path + self.voice_name_dict["SystemVoice"][name])
        self.system_play_handle.start()
        self.system_play_handle.join()#等待音频播放完
    #开启语音识别线程
    def start_audio_recognize(self, input_queue,output_queue):
        self.audio_recognize_handle =AudioRecognizeWebsocket(input_queue,output_queue)
        self.audio_recognize_handle.start()
    def close_audio_recognize(self):
        if self.audio_recognize_handle != None:
            self.audio_recognize_handle = None
    def start_audio_long_recognize(self, input_queue,output_queue):
        self.audio_recognize_handle =speech_recognition_Process(input_queue,output_queue)
        self.audio_recognize_handle.start()


class SafeExamProcess(BaseVoicePlay, Process):
    def __init__(self):
        BaseVoicePlay.__init__(self)
        Process.__init__(self)
        self.question_number = 8
        self.audio_recognize_output_queue = Queue()
        self.audio_recognize_input_queue = Queue()
        self.exam_number = 4
        
    def jaccard_judge(self,input_answer, correct_answer):
        a = set(list(input_answer))
        b = set(list(correct_answer))
        c = a.intersection(b) #取交集
        return float(len(c))/len(b)
        # return float(len(c)) / (len(a) + len(b) - len(c)) #相似度算法

    #返回随机选择的题目编号的列表 list
    def random_choice_question(self,exam_number): #exam_number代表要生成的随机数的个数
        random_question_list = []
        if exam_number >= self.question_number: #要生成的数量大于或者等于题库总数
            for i in range(self.question_number):
                random_question_list.append(i+1)
                return random_question_list

        try:
            while True:
                number = random.randint(1,self.question_number)
                if number not in random_question_list:
                    random_question_list.append(number)
                if len(random_question_list) >= exam_number:
                    return random_question_list
        except Exception as e:
            print("random choice question error:",e)
            return []
    #判断答案函数
    def judeg_answer(self,question_lib_name,number):
        correct_answer = self.voice_name_dict[question_lib_name][number]["answer"]
        print(correct_answer)
        min_len = 0.8*len(correct_answer)
        # print(min_len)
        all_answers = ''
        begin_date_time = datetime.datetime.now()
        while True:
            try:
                if (datetime.datetime.now() - begin_date_time).seconds > 20:
                    self.audio_recognize_input_queue.put("process_end")
                    print("回答超时，退出操作")
                    return False
            except Exception as e:
                print(e)
            try:
                unit_answers = self.audio_recognize_output_queue.get(False)
                # print("ghghg:" + unit_answers)
                if unit_answers == 'timeout':
                    return False
                if "不知道" in unit_answers:
                    self.audio_recognize_input_queue.put("process_end")
                    # print("nmd不会")
                    return False
                all_answers += unit_answers

                if self.jaccard_judge(all_answers,correct_answer) > 0.75: #如果包含答案
                    if min_len < len(all_answers):
                        # print("回答正确,退出操作")
                        self.audio_recognize_input_queue.put("process_end")
                        return True
                else:
                    if len(all_answers) > (1.2*len(correct_answer)):
                        # print("回答错误,退出操作")
                        self.audio_recognize_input_queue.put("process_end")
                        return False
            except Exception as e:
                # print("ok",e)
                time.sleep(1)

    def run(self):
        self.play_system_audio("考核开始")
        choiced_question_list = self.random_choice_question(self.exam_number)
        print(choiced_question_list)
        correct_num = 0
        #考试流程
        for num in choiced_question_list:
            self.play_question_audio("安全知识题库",num - 1)#播放题目
            self.start_audio_recognize(self.audio_recognize_input_queue, self.audio_recognize_output_queue)#开启语音识别线程
            if self.judeg_answer("安全知识题库",num - 1):
                correct_num = correct_num + 1
                self.play_system_audio("回答正确")
            else:
                self.play_system_audio("回答错误")
            time.sleep(2)
            self.close_audio_recognize()

        self.play_system_audio("考核结束")
        if (float(correct_num)/self.exam_number) > 0.59:
            self.play_system_audio("考核通过")
        else:
            self.play_system_audio("考核没通过")


class RobotAwakeProcess(Process,BaseVoicePlay):
    def __init__(self,ip_port,cmd_queue):
        BaseVoicePlay.__init__(self)
        Process.__init__(self)
        self.ip_port = ip_port
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #接收音频信号
        self.cmd_queue = cmd_queue
    
    def cmd_slect(self):
        try:
            all_answers = self.cmd_queue.get() #阻塞等待

            if "开始考核" in all_answers: #如果包含答案
                # print("考核操作")
                exam_process = SafeExamProcess()
                exam_process.start()
                exam_process.join()
        except Exception as e:
            print("cmd_slect",e)

    def run(self):
        # self.receive_socket.bind(self.ip_port)
        while True:
            try:
                self.cmd_slect()
            except Exception:
                pass

# if __name__ == "__main__":
#     # 测试时候在此处正确填写相关信息即可运行
#     time1 = datetime.datetime.now()
#     testprocess = SafeExamProcess()
#     testprocess.start()
#     # while True:
#     #     if not testprocess.is_alive():
#     #         break
#     #     time.sleep(1)
#     testprocess.join()
#     time2 = datetime.datetime.now()
#     print(time2-time1)