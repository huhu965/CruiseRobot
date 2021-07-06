#ifndef _VIDEOHANDLE_H_ 
#define _VIDEOHANDLE_H_

#include "msp_cmn.h"
#include "qivw.h"
#include "msp_errors.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <cstdlib>
#include <iostream>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <string.h>
#include <vector>
#include <pthread.h>
#include <map>
#include <string>

#include <opencv2/opencv.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui_c.h>

#include "HCNetSDK.h"
#include "LinuxPlayM4.h"

#include "alsa/asoundlib.h" 
#define begin_trans 22
#define end_trans 23
#define heart_test 24

//函数指针
typedef void (*create_fun)(void* args);

//头格式帧
typedef struct{  
unsigned int dwDataType; //要传输的数据类型
unsigned int dwBufSize; //要传输的数据大小
}HeadData;

//摄像头相关参数，结构体不能给初值
typedef struct
{
    LONG lUserID;
    LONG lRealPlayHandle;
    LONG nPort;
    LONG lTemperatureHandle;
    NET_DVR_DEVICEINFO_V30 struDeviceInfo;//注册设备结构
    NET_DVR_PREVIEWINFO struPlayInfo;//预览结构
    std::string register_identity;

    char *addrcream;
    char *name;
    char *password;
    bool transforming_video = false;
    bool heart_respond = false;
    bool have_voice = false;

    int socket_tcp;//视频传输socket
    int socket_udp;//视频传输socket
    struct sockaddr_in server_addr; //服务器地址
    struct sockaddr_in udp_server_addr; //服务器地址
    /*udp*/
    int command_receive_socket;
    struct sockaddr_in command_addr; //socket地址参数等
    /*udp*/
    int voice_upload_socket;//音频传输
    struct sockaddr_in voice_addr; //服务器地址
    struct sockaddr_in voice_cmd_addr;//唤醒后给主线程发送唤醒指令

    char data_buff[10000];  //视频信息缓冲
    int data_buff_size;
    int data_stamp;

}CameraParam,* CameraParamPtr;

//语音识别相关参数，结构体不能给初值
typedef struct
{
    const char *login_param; //常量指针，指针指向可以改，但不能通过指针修改内容
    const char *session_begin_params;
    const char *session_id;//每次唤醒时的句柄
    const char *grammar_list;//保留参数，设为null
    int audio_stat; //标记数据帧是开始还是结束
    bool is_awake; //标记是否唤醒

}VoiceAwakeParam,* VoiceAwakeParamPtr;

typedef struct
{
    LONG lUserID;
    DWORD dwPTZCommand;
    DWORD dwStop;
    DWORD dwSpeed;
}PTZParam,* PTZParamPtr;
/*------------内部函数，给定参数都是结构体----------*/
/*图片格式转换*/
std::string  transform_TYV12_to_CV8UC3(char * pBuf, int nSize, FRAME_INFO * pFrameInfo);
/*音频8k转16k*/
void Resample16K(short* pInAudioData, int nInAudioLen, short* pOutAudioData, int& nOutAudioLen);
/*语音唤醒回调函数*/
int cb_ivw_msg_proc( const char *sessionID, int msg, int param1, int param2, const void *info, void *userData);
/*解码完成回调函数*/
void CALLBACK infrared_DecCBFun(int nPort, char * pBuf, int nSize, FRAME_INFO * pFrameInfo, void* nReserved1,int nReserved2);
void CALLBACK normal_DecCBFun(int nPort, char * pBuf, int nSize, FRAME_INFO * pFrameInfo, void* nReserved1,int nReserved2);
void CALLBACK voice_DecCBFun(int nPort, char * pBuf, int nSize, FRAME_INFO * pFrameInfo, void* nReserved1,int nReserved2);
/*异常回调函数*/
void CALLBACK g_ExceptionCallBack(DWORD dwType, LONG lUserID, LONG lHandle, void *pUser);
/*视频流回调函数*/
void CALLBACK fRealDataCallBack(LONG lRealHandle, DWORD dwDataType, BYTE *pBuffer, DWORD dwBufSize, void *pUser);
/*云台控制函数*/
void _PTZ_control(void* args);
/*打开视频函数*/
void _video_begin(void* args);
/*关闭视频函数*/
void _video_stop(void* args);
/*连接服务器函数*/
void _connect_server(void* args);
/*断开服务器链接函数*/
void _disconnect_server(void* args);
/*构建指令接收服务器*/
void _build_cmd_server(void* args);
/*关闭指令接收服务器*/
void _close_cmd_server(void* args);
/*登录摄像头*/
void _login_camera(void* args);
/*建立读取温度长链接*/
void _read_temperature(void* args);
/*语音被唤醒后恢复休眠等待下一次唤醒*/
void _voice_sleep(void* args);
/*字符串分割函数*/
std::vector<std::string> split(std::string str, std::string pattern);
std::map<std::string, std::string> split_url_param(std::string url_param);

extern CameraParam normal_camera;
extern CameraParam infrared_camera;
extern std::map<std::string, create_fun> FunctionMap;
extern VoiceAwakeParam awake_param;
/*------------开放给web调用函数，给定参数都是字符串----------*/
/*云台控制函数*/
void PTZ_control(void* args);
/*打开视频函数*/
void video_begin(void* args);
/*关闭视频函数*/
void video_stop(void* args);
/*语音被唤醒后恢复休眠等待下一次唤醒*/
void voice_sleep(void* args);

// void* getClassByName(std::string name){

// std::map<std::string, create_fun>::iterator it = my_map.find(name);
// if (it == my_map.end()) { return NULL; }

// create_fun fun = it->second;
// if (!fun) { return NULL; }
 
// return fun();
// }   

// //注册类名称与指针函数到映射关系
// void registClass(std::string name, create_fun fun){
// my_map[name] = fun;
// } 
#endif //_VIDEOHANDLE_H_
