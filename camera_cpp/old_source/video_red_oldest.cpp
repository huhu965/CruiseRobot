#include <stdio.h>
#include <cstdlib>
#include <iostream>
#include <cstring>
#include "HCNetSDK.h"
#include "LinuxPlayM4.h"
#include <time.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <vector>
#include <pthread.h>
#include <signal.h>
using namespace std;

#define begin_trans 22
#define end_trans 23

int socket_fd = socket(AF_INET, SOCK_STREAM, 0);  //tcp通信，发送视频
struct sockaddr_in addr; //socket地址参数等
char data_Buffer[10000]; //发送缓冲区

LONG lUserID;
LONG lRealPlayHandle;

struct Data {  //头格式帧
  unsigned int dwDataType;
  unsigned int dwBufSize;
 }headdata,recv_head_data;

void CALLBACK fRealDataCallBack(LONG lRealHandle, DWORD dwDataType, BYTE *pBuffer, DWORD dwBufSize, void *pUser)
{
    memset(data_Buffer, 0, sizeof(data_Buffer)); //清空
    headdata.dwDataType = dwDataType;
    headdata.dwBufSize = dwBufSize;
    memcpy(data_Buffer,pBuffer,dwBufSize);
    int num_1 = send(socket_fd, (char*)&headdata, sizeof(struct Data), MSG_WAITALL);
    int num = send(socket_fd,data_Buffer,dwBufSize,MSG_WAITALL);//通过tcp直接发送码流
    // cout<<num_1<<" "<<num<<endl;
}

void CALLBACK g_ExceptionCallBack(DWORD dwType, LONG lUserID, LONG lHandle, void *pUser)
{
    char tempbuf[256] = { 0 };
    switch (dwType)
    {
    case EXCEPTION_RECONNECT:    //预览时重连
        // printf("----------reconnect--------%d\n", time(NULL));
        break;
    default:
        break;
    }
}


void my_exit(int sig)
{
    close(socket_fd);
    //关闭预览
    NET_DVR_StopRealPlay(lRealPlayHandle);
    //注销用户
    NET_DVR_Logout(lUserID);
    //释放SDK资源
    NET_DVR_Cleanup();
    exit(sig);
}


int main()
{
    memset(&addr, 0, sizeof(addr)); 
    addr.sin_family = AF_INET;
    addr.sin_port = htons(62222);//将一个无符号短整型的主机数值转换为网络字节顺序，即大尾顺序(big-endian)
    addr.sin_addr.s_addr = inet_addr("101.37.16.240");
    signal(SIGINT, my_exit); // 设置信号
    sleep(120);
    //循环链接
    while(connect(socket_fd, (struct sockaddr *)&addr, sizeof(struct sockaddr)) < 0)
    {
        perror("connect error");
        cout<<"服务器不在线"<<endl;
        sleep(5);
    }

    // headdata.dwDataType = 24;  //20表示机器人
    // headdata.dwBufSize = 0;
    string register_identity = "robot_video_red \r\n";
    send(socket_fd, register_identity.c_str(), register_identity.length(), MSG_WAITALL); //向服务器端注册是机器人
    //---------------------------------------
    // 初始化
    NET_DVR_Init();
    //设置连接时间与重连时间
    NET_DVR_SetConnectTime(2000, 1);
    NET_DVR_SetReconnect(10000, true);
    //---------------------------------------
    // 注册设备
    NET_DVR_DEVICEINFO_V30 struDeviceInfo;
    char addrcream[] = "10.7.5.122";
    char name[] = "admin";
    char password[] = "sgkj123456";
    //---------------------------------------
    //设置异常消息回调函数
    NET_DVR_SetExceptionCallBack_V30(0, NULL, g_ExceptionCallBack, NULL);
    //---------------------------------------
    //启动预览并设置回调数据流
    NET_DVR_PREVIEWINFO struPlayInfo = { 0 };
    struPlayInfo.hPlayWnd = NULL;         //需要SDK解码时句柄设为有效值，仅取流不解码时可设为空
    struPlayInfo.lChannel = 1;           //预览通道号
    struPlayInfo.dwStreamType = 1;       //0-主码流，1-子码流，2-码流3，3-码流4，以此类推
    struPlayInfo.dwLinkMode = 1;         //0- TCP方式，1- UDP方式，2- 多播方式，3- RTP方式，4-RTP/RTSP，5-RSTP/HTTP
    struPlayInfo.bBlocked = 0; //0- 非阻塞取流， 1- 阻塞取流

        //登录摄像头
    while(1)
    {
        lUserID = NET_DVR_Login_V30(addrcream, 8000, name, password, &struDeviceInfo);//登录摄像头
        if (lUserID < 0)
        {
            printf("Login error, %d\n", NET_DVR_GetLastError());
            sleep(10);
        }
        else
        {
            break;
        }
    }


    while(true)
    {
        memset(&recv_head_data, 0, sizeof(struct Data)); //清空
        recv(socket_fd, (char*)&recv_head_data, sizeof(struct Data), MSG_WAITALL);
        if(recv_head_data.dwDataType == begin_trans)
        {
            cout<<"begin"<<endl;
            //开始实时预览
            lRealPlayHandle = NET_DVR_RealPlay_V40(lUserID, &struPlayInfo, fRealDataCallBack, NULL);//开始取流解码
            if (lRealPlayHandle < 0){
                printf("NET_DVR_RealPlay_V40 error\n");
                printf("%d\n", NET_DVR_GetLastError());
            }
        }
        else if(recv_head_data.dwDataType == end_trans)
        {
            cout<<"end"<<endl;
            NET_DVR_StopRealPlay(lRealPlayHandle);
        }
    }
    
    // waitKey();
    //---------------------------------------
    //关闭预览
    NET_DVR_StopRealPlay(lRealPlayHandle);
    //注销用户
    NET_DVR_Logout(lUserID);
    //释放SDK资源
    NET_DVR_Cleanup();
    return 0;
}