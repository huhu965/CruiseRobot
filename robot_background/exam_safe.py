import socket
import os
import sys
import threading
import time
import datetime
import json
from threading import Thread
from multiprocessing import Process
from play_voice import PlayVoice
import random
class exam_safe_Process(Process):
    def __init__(self):
        super(exam_safe_Process, self).__init__()
        self.process_is_alive = True #进程是否活着
        self.question_number = 10
        
    def jaccard_judge(self,input_answer, correct_answer):
        a = set(list(input_answer))
        b = set(list(correct_answer))
        c = a.intersection(b) #取交集
        return float(len(c)) / (len(a) + len(b) - len(c))

    #返回随机选择的题目编号的列表
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

    def run(self):
        self.voice_play = PlayVoice("考核开始")
        choiced_question_list = random_choice_question(5)
        for num in choiced_question_list:
            voice_play_handle = PlayVoice(str(num)) #播放题号
            while True:         #等待播放完成
                if voice_play_handle.is_playing():
                    time.sleep(0.5)
                else:
                    break
        