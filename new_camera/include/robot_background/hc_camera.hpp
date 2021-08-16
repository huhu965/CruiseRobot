/* 
 * @Author: Hu Ziwei
 * @Description: 摄像头相关
 * @Date: 2021-07-15 20:01:46
 * @Last Modified by: Hu Ziwei
 * @Last Modified time: 2021-07-16 00:40:17
 * @命名规则
 *   1.类名和方法命名用驼峰，FunName
 *   2.类内变量，全部小写，下划线分割，param_name
 *   3.类内私有的变量和方法统一在最后加下划线，FunNam_;param_name_
 *   4.函数内临时变量统一在前面加下划线，_param_name
 *   5.方法名带数字驼峰不好阅读时，加_下划线分割，Transform_Tyv12_To_Cv8uc3
*/
#ifndef ROBOT_BACKGROUND_HC_CAMERA_HPP_
#define ROBOT_BACKGROUND_HC_CAMERA_HPP_

#include "robot_background/base_func.hpp"

#include <iostream>
#include "string"
#include <unistd.h>

#include "hc/HCNetSDK.h"
#include "hc/LinuxPlayM4.h"


namespace robot_background{
/*
 * @Description:设置从设备读取的音频格式，0是编码后数据，1是原始pcm数据
*/
#define AUDIO_DATA_TYPE 1 
/*
 * @Description:摄像头相关参数结构体，结构体不能给默认初值
*/
typedef struct
{
    LONG lUserID;//登录返回值
    LONG lRealPlayHandle;//播放视频返回值
    LONG nPort; //playm4解码器返回值
    LONG lTemperatureHandle; //温度读取返回值
    LONG lVoiceHanle; //音频读取返回值
    NET_DVR_DEVICEINFO_V30 struDeviceInfo;//注册设备结构体
    NET_DVR_PREVIEWINFO struPlayInfo;//预览结构体

    char *addr_camera; //摄像头ip地址
    char *name; //用户名
    char *password; //密码
}CameraParam,* CameraParamPtr;

/*
 * @Description:存放海康摄像头操作的类
*/
class HcCameraHandle{
    public:
        HcCameraHandle() = default;
        HcCameraHandle(CameraParam camera_param);
        ~HcCameraHandle() = default;
        /////////////摄像头功能函数//////////////
        /*
         * @Description:登录摄像头
        */
        void LogIn();
        /*
         * @Description:退出摄像头
        */
        void LogOut();
        /*
         * @Description:打开读取温度
        */
        virtual void ReadTemperature();
        /*
         * @Description:关闭读取温度
        */
        void CloseReadTemperature();
        /*
         * @Description:打开音频读取
        */
        virtual void ReadVoice();
        /*
         * @Description:关闭音频读取
        */
        void CloseReadVoice();
        /*
         * @Description:云台控制
        */
        void PTZControl(void* args);
        /*
         * @Description:开始视频传输
        */
        void VideoBegin();
        /*
         * @Description:关闭视频传输
        */
        void VideoStop();

        /////////////回调函数//////////////
        /*
         * @Description:温度数据回调函数
        */
        static void CALLBACK RemoteConfigCallback(DWORD dwType, void *lpBuffer, DWORD dwBufLen, void *pUserData);
        /*
         * @Description:音频回调函数
        */
        static void CALLBACK fVoiceDataCallBack(LONG lVoiceComHandle, 
                                                char *pRecvDataBuffer, 
                                                DWORD dwBufSize, 
                                                BYTE byAudioFlag, 
                                                void*pUser);
        /*
         * @Description:音视频流回调函数
        */
        static void CALLBACK fRealDataCallBack(LONG lRealHandle, 
                                                DWORD dwDataType, 
                                                BYTE *pBuffer, 
                                                DWORD dwBufSize, 
                                                void *pUser);
        /*
         * @Description:异常回调函数
        */
        static void CALLBACK g_ExceptionCallBack(DWORD dwType, LONG lUserID, LONG lHandle, void *pUser);
        /*
         * @Description:用于PlayM4_SetDecCallBack，复合流解码完成回调函数,只给出接口，用的时候再去定义实现
        */
        static void CALLBACK VideoDataDecCBFun(int nPort, 
                                                char * pBuf, 
                                                int nSize, 
                                                FRAME_INFO * pFrameInfo, 
                                                void* nReserved1, 
                                                int nReserved2);
                                                
    protected:
        std::string format = "Int16"; //音频格式
        int audio_rate_ = 8000; //音频采样率
        int channles = 1;  //音频通道数目
        CameraParam camera_param;  //摄像头参数
};

}

#endif