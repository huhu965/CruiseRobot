/* 
 * @Author: Hu Ziwei
 * @Description: 测试功能用的
 * @Date: 2021-07-16 00:23:45
 * @Last Modified by: Hu Ziwei
 * @Last Modified time: 2021-07-19 21:31:57
 * @命名规则
 *   1.类名和方法命名用Pascal ，FunName
 *   2.类内变量，全部小写，下划线分割，param_name
 *   3.类内私有的变量和方法统一在最后加下划线，FunNam_;param_name_
 *   4.函数内临时变量统一在前面加下划线，_param_name
 *   5.方法名带数字驼峰不好阅读时，加_下划线分割，Transform_Tyv12_To_Cv8uc3
*/

#include <signal.h>
#include <unistd.h>
#include <memory>

#include "robot_background/network_hc_camera.hpp"

using namespace robot_background;

bool process_run = true;

void MySigintHandler(int sig){
    process_run = false;
}

int main(int argc, char *argv[]){

    if(!NET_DVR_Init()){ //摄像头资源初始化
        std::cout<<"摄像头资源初始化失败，错误值："<<NET_DVR_GetLastError()<<std::endl;
    }else{
        std::cout<<"摄像头资源初始化成功！"<<std::endl;
    }
    NET_DVR_SetConnectTime(2000, 1);//设置连接时间与重连时间
    NET_DVR_SetReconnect(10000, true);
    NET_DVR_SetExceptionCallBack_V30(0, NULL, HcCameraHandle::g_ExceptionCallBack, NULL);//设置异常回调函数

    signal(SIGINT, MySigintHandler);

    CameraParam camera_param;
    NetworkSocketParam network_param;
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    NET_DVR_PREVIEWINFO struPlayInfo = {0};

    //登录结构体初始化
    struPlayInfo.hPlayWnd = NULL;        //需要SDK解码时句柄设为有效值，仅取流不解码时可设为空
    struPlayInfo.lChannel = 1;           //预览通道号
    struPlayInfo.dwStreamType = 1;       //0-主码流，1-子码流，2-码流3，3-码流4，以此类推
    struPlayInfo.dwLinkMode = 1;         //0- TCP方式，1- UDP方式，2- 多播方式，3- RTP方式，4-RTP/RTSP，5-RSTP/HTTP
    struPlayInfo.bBlocked = 0;           //0- 非阻塞取流， 1- 阻塞取流
    //摄像头参数初始化
    camera_param.struPlayInfo = struPlayInfo;
    camera_param.addr_camera = (char*)"10.7.5.121";
    camera_param.name = (char*)"admin";
    camera_param.password = (char*)"sgkj123456";
    //设置指令接收地址
    network_param.udp_command_socket = socket(AF_INET, SOCK_DGRAM, 0);
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8002);//将一个无符号短整型的主机数值转换为网络字节顺序，即大尾顺序(big-endian)
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    network_param.udp_command_addr = addr;

    //音频传输网络初始
    network_param.udp_client_socket = socket(AF_INET, SOCK_DGRAM, 0);
    addr.sin_port = htons(8021);
    network_param.udp_server_addr = addr;
    std::shared_ptr<NetworkHcCameraHandle> voice_pub_ptr = std::make_shared<NetworkHcCameraHandle>(camera_param, network_param);
    voice_pub_ptr->ReadVoice();
    voice_pub_ptr->BuildCmdServer();

    //温度传输
    camera_param.addr_camera = (char*)"10.7.5.122";

    network_param.udp_client_socket = socket(AF_INET, SOCK_DGRAM, 0);
    addr.sin_port = htons(8022);
    network_param.udp_server_addr = addr;
    std::shared_ptr<NetworkHcCameraHandle> temp_pub_ptr = std::make_shared<NetworkHcCameraHandle>(camera_param, network_param);
    temp_pub_ptr->ReadTemperature();

    while(process_run){
        voice_pub_ptr->CmdHandle();
    }

    voice_pub_ptr->CloseReadVoice();
    voice_pub_ptr->LogOut();
    temp_pub_ptr->CloseReadTemperature();
    temp_pub_ptr->LogOut();
    //释放SDK资源
    NET_DVR_Cleanup();
    std::cout<<"摄像头资源释放成功！"<<std::endl;
    return 0;
}