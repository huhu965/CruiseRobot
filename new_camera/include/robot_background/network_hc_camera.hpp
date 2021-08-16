/* 
 * @Author: Hu Ziwei
 * @Description: 温度发布
 * @Date: 2021-07-15 20:03:08
 * @Last Modified by: Hu Ziwei
 * @Last Modified time: 2021-07-19 15:03:40
 * @命名规则
 *   1.类名和方法命名用驼峰，FunName
 *   2.类内变量，全部小写，下划线分割，param_name
 *   3.类内私有的变量和方法统一在最后加下划线，FunNam_;param_name_
 *   4.函数内临时变量统一在前面加下划线，_param_name
 *   5.方法名带数字驼峰不好阅读时，加_下划线分割，Transform_Tyv12_To_Cv8uc3
*/
#ifndef ROBOT_BACKGROUND_NETWORK_HC_CAMERA_HPP_
#define ROBOT_BACKGROUND_NETWORK_HC_CAMERA_HPP_

#include <string>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>


#include "robot_background/hc_camera.hpp"


namespace robot_background {
/*
 * @Description:摄像头相关参数结构体，结构体不能给默认初值
*/
typedef struct
{
    int tcp_client_socket;
    struct sockaddr_in tcp_server_addr; //服务器地址

    int udp_client_socket;
    struct sockaddr_in udp_server_addr; //服务器地址
    /*udp,接收命令*/
    int udp_command_socket;
    struct sockaddr_in udp_command_addr; //socket地址参数等

}NetworkSocketParam,* NetworkSocketParamPtr;

class NetworkHcCameraHandle:public HcCameraHandle{
    public:
        NetworkHcCameraHandle(CameraParam camera_param,NetworkSocketParam network_socket_param);
        NetworkHcCameraHandle() = default;
        ~NetworkHcCameraHandle() = default;

        void Close();

        /*
        * @Description:打开温度读取，针对红外摄像头
        */
        void ReadTemperature();
        /*
            * @Description:打开音频读取
        */
        void ReadVoice();
        /*
            * @Description:构建指令接收
        */
        void BuildCmdServer();
        /*
            * @Description:接收指令
        */
        void CmdHandle();
        /*
        * @Description:温度回调函数
        */
        static void CALLBACK RemoteConfigCallback(DWORD dwType, void *lpBuffer, DWORD dwBufLen, void *pUserData);
        /*
        * @Description:声音回调函数
        */
        static void CALLBACK fVoiceDataCallBack(LONG lVoiceComHandle, 
                                        char *pRecvDataBuffer, 
                                        DWORD dwBufSize, 
                                        BYTE byAudioFlag, 
                                        void*pUser);
    private:
        NetworkSocketParam network_socket_param_;
};
}
#endif

