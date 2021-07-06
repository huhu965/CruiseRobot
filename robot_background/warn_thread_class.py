from play_voice import PlayVoice, play_system_audio
from threading import Thread
import time
#温度报警函数
#device_data_upload_thread 是数据采集线程
class TemperatureWarnThread(Thread):
    def __init__(self, device_data_upload_thread):
        super().__init__()
        self.device_data_upload_thread = device_data_upload_thread

    def run(self):
        while True:
            max_temperature = self.device_data_upload_thread.get_max_temperature()
            if max_temperature > 100:
                play_system_audio("环境高温警告")
            time.sleep(1)

#气体浓度报警函数
#device_data_upload_thread 是数据采集线程
class GasWarnThread(Thread):
    def __init__(self, device_data_upload_thread):
        super().__init__()
        self.device_data_upload_thread = device_data_upload_thread

    def run(self):
        while True:
            sensor1,sensor2 = self.device_data_upload_thread.get_sensor_concentration()
            if sensor1>25 or sensor2>25:
                play_system_audio("气体浓度超标警告")
            time.sleep(1)