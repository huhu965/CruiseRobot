import serial
import time
import datetime
import threading
import json

# date_now = datetime.datetime.now()
# print(date_now)
# print(type(date_now))
# time.sleep(2)
# date_2 = datetime.datetime.now()
# print(date_2)
# print(type(date_2))
# print((date_2-date_now).seconds)
# ser=serial.Serial("/dev/ttyUSB0",9600,timeout=0.5) #使用USB连接串行口
# cmd = '01 04 00 00 00 08 F1 CC' #读数据命令

# while True:
#     d=bytes.fromhex(cmd)
#     ser.write(d)
#     data= ser.readall() 
#     print(data)
#     read_data1 =int.from_bytes(data[3:5],byteorder='big',signed=False)
#     read_data2 =int.from_bytes(data[5:7],byteorder='big',signed=False)
#     print(read_data1,read_data2)
#     actual_data1 = round((read_data1 - 819)*100/(4096-819))
#     actual_data2 = round((read_data2 - 819)*100/(4096-819))  
#     if actual_data1 < 0:
#         actual_data1 = 0
#     if actual_data2 < 0:
#         actual_data2 = 0    
#     print(actual_data1,actual_data2)
#     time.sleep(1)
# ser.close()

# ser.close()

t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(type(t),t)