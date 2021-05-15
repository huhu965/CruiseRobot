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
#include "VideoHandle.h"
using namespace std;


//头格式帧
struct Data {  
unsigned int dwDataType;
unsigned int dwBufSize;
}headdata,recv_head_data;
//摄像头相关参数
LONG lUserID;
LONG lRealPlayHandle;  
//tcp通信，发送视频
int socket_fd = socket(AF_INET, SOCK_STREAM, 0);
struct sockaddr_in addr; //socket地址参数等
char data_Buffer[10000]; //发送缓冲区
//udp服务器
int socket_ptz = socket(AF_INET, SOCK_DGRAM, 0);  
struct sockaddr_in addr_ptz; //socket地址参数等
char ptz_recv_Buffer[256]; //发送缓冲区
// 注册设备
NET_DVR_DEVICEINFO_V30 struDeviceInfo;
char addrcream[] = "10.7.5.121";
char name[] = "admin";
char password[] = "sgkj123456";
//启动预览并设置回调数据流
NET_DVR_PREVIEWINFO struPlayInfo = { 0 };
//云台接收指令线程
pthread_t cmd_recv_threads;
//心跳发送线程
pthread_t heart_send_threads;
//接收到心跳验证
bool receive_heart_respond = false;
bool transforming_video = false;

void *receive_ptz_cmd(void* args);//云台控制回调函数
void *heart_thread(void* args);//心跳线程
void CALLBACK fRealDataCallBack(LONG lRealHandle, DWORD dwDataType, BYTE *pBuffer, DWORD dwBufSize, void *pUser);
void CALLBACK g_ExceptionCallBack(DWORD dwType, LONG lUserID, LONG lHandle, void *pUser);
void my_exit(int sig);//接收退出信号后收尾退出程序
void param_init();//参数初始化
void connect_server();//链接服务器
void build_ptz_server();//接收云台指令服务器
void connect_camera();//链接摄像头
void Init();//程序初始化
void run();//程序运行
void send_heart();//发送心跳信息
//发送心跳
void send_heart(){
    headdata.dwDataType = 24;
    headdata.dwBufSize = 0;
    send(socket_fd, (char*)&headdata, sizeof(struct Data), MSG_WAITALL);
}
//心跳线程
void *heart_thread(void* args){
    while (true)
    {
        if(transforming_video == false)
        {
            send_heart();
            receive_heart_respond = false;
        }
        sleep(10);
        if(receive_heart_respond == false)
        {
            cout<<"链接断开"<<endl;
            my_exit(SIGINT);
        }
    }
}
//云台调用
//ZOOM_IN 焦距变大
//ZOOM_OUT 焦距变小
void *receive_ptz_cmd(void* args){
    // long lUserID = *(int*)args;
    cout<<lUserID<<"yuntai"<<endl;
    while(true){
        //最后一个参数可能有问题，测得时候再说,接收看能不能用字符串
        memset(ptz_recv_Buffer, 0, sizeof(ptz_recv_Buffer)); //清空
        int recv_num = recvfrom(socket_ptz, ptz_recv_Buffer, sizeof(ptz_recv_Buffer), 0, (struct sockaddr *)&addr_ptz, (socklen_t *)sizeof(struct sockaddr));
        if(strcmp("up",ptz_recv_Buffer) == 0){
            NET_DVR_PTZControlWithSpeed_Other(lUserID,1,TILT_UP,0,2);
            sleep(2);
            NET_DVR_PTZControlWithSpeed_Other(lUserID,1,TILT_UP,1,2);
        }
        if(strcmp("down",ptz_recv_Buffer) == 0){
            NET_DVR_PTZControlWithSpeed_Other(lUserID,1,TILT_DOWN,0,2);
            sleep(2);
            NET_DVR_PTZControlWithSpeed_Other(lUserID,1,TILT_DOWN,1,2);
        }
        if(strcmp("left",ptz_recv_Buffer) == 0){
            NET_DVR_PTZControlWithSpeed_Other(lUserID,1,PAN_LEFT,0,2);
            sleep(3);
            NET_DVR_PTZControlWithSpeed_Other(lUserID,1,PAN_LEFT,1,2);
        }
        if(strcmp("right",ptz_recv_Buffer) == 0){
            NET_DVR_PTZControlWithSpeed_Other(lUserID,1,PAN_RIGHT,0,2);
            sleep(3);
            NET_DVR_PTZControlWithSpeed_Other(lUserID,1,PAN_RIGHT,1,2);
        }
    }
    pthread_exit(NULL);
}
// 实时流回调
void CALLBACK fRealDataCallBack(LONG lRealHandle, DWORD dwDataType, BYTE *pBuffer, DWORD dwBufSize, void *pUser){
    memset(data_Buffer, 0, sizeof(data_Buffer)); //清空
    headdata.dwDataType = dwDataType;
    headdata.dwBufSize = dwBufSize;
    memcpy(data_Buffer,pBuffer,dwBufSize);
    int num_1 = send(socket_fd, (char*)&headdata, sizeof(struct Data), MSG_WAITALL);
    int num = send(socket_fd,data_Buffer,dwBufSize,MSG_WAITALL);//通过tcp直接发送码流
}

void CALLBACK g_ExceptionCallBack(DWORD dwType, LONG lUserID, LONG lHandle, void *pUser){
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
//退出收尾函数
void my_exit(int sig){
    close(socket_fd);
    close(socket_ptz);
    //关闭预览
    NET_DVR_StopRealPlay(lRealPlayHandle);
    //注销用户
    NET_DVR_Logout(lUserID);
    //释放SDK资源
    NET_DVR_Cleanup();
    exit(sig);
}
//参数初始化
void param_init(){
    memset(&addr, 0, sizeof(addr)); 
    addr.sin_family = AF_INET;
    addr.sin_port = htons(62222);//将一个无符号短整型的主机数值转换为网络字节顺序，即大尾顺序(big-endian)
    addr.sin_addr.s_addr = inet_addr("101.37.16.240");

    memset(&addr_ptz, 0, sizeof(addr_ptz));
    addr_ptz.sin_family = AF_INET;
    addr_ptz.sin_port = htons(8002);//将一个无符号短整型的主机数值转换为网络字节顺序，即大尾顺序(big-endian)
    addr_ptz.sin_addr.s_addr = inet_addr("127.0.0.1");
    //登录结构体
    struPlayInfo.hPlayWnd = NULL;         //需要SDK解码时句柄设为有效值，仅取流不解码时可设为空
    struPlayInfo.lChannel = 1;           //预览通道号
    struPlayInfo.dwStreamType = 1;       //0-主码流，1-子码流，2-码流3，3-码流4，以此类推
    struPlayInfo.dwLinkMode = 1;         //0- TCP方式，1- UDP方式，2- 多播方式，3- RTP方式，4-RTP/RTSP，5-RSTP/HTTP
    struPlayInfo.bBlocked = 0; //0- 非阻塞取流， 1- 阻塞取流
}
//链接服务器
void connect_server(){
    while(connect(socket_fd, (struct sockaddr *)&addr, sizeof(struct sockaddr)) < 0)
    {
        perror("connect error");
        cout<<"服务器不在线"<<endl;
        sleep(5);
    }
    string register_identity = "robot_video \r\n";
    send(socket_fd, register_identity.c_str(), register_identity.length(), MSG_WAITALL); //向服务器端注册是机器人
}
//构建云台指令接收服务器
void build_ptz_server(){
    //绑定udp接收
    if(bind(socket_ptz, (struct sockaddr *)&addr_ptz, sizeof(struct sockaddr)) < 0){
        cout<<"server connect error"<<endl;
    }
}
//登录摄像头
void connect_camera(){
    while(1){
        lUserID = NET_DVR_Login_V30(addrcream, 8000, name, password, &struDeviceInfo);//登录摄像头
        if (lUserID < 0){
            printf("Login error, %d\n", NET_DVR_GetLastError());
            sleep(10);
        }
        else{
            break;
        }
    }
}
//程序初始化函数
void Init(){
        //---------------------------------------
    //摄像头资源初始化
    NET_DVR_Init();
    //设置连接时间与重连时间
    NET_DVR_SetConnectTime(2000, 1);
    NET_DVR_SetReconnect(10000, true);
    //---------------------------------------
    NET_DVR_SetExceptionCallBack_V30(0, NULL, g_ExceptionCallBack, NULL);

    signal(SIGINT, my_exit); // 设置信号

    param_init();
    connect_server();
    build_ptz_server();
    connect_camera();
    int rc = pthread_create(&cmd_recv_threads, NULL, receive_ptz_cmd,&lUserID);//创建接收命令线程
    if (rc){
        cout << "Error:无法创建线程:" << rc << endl;
    }
    int rc2 = pthread_create(&heart_send_threads, NULL, heart_thread,&lUserID);//创建接收命令线程
    if (rc2){
        cout << "Error:无法创建线程:" << rc2 << endl;
    }
}

void run(){
    while(true){
        memset(&recv_head_data, 0, sizeof(struct Data)); //清空
        recv(socket_fd, (char*)&recv_head_data, sizeof(struct Data), MSG_WAITALL);
        if(recv_head_data.dwDataType == begin_trans)
        {
            cout<<"begin"<<endl;
            transforming_video = true;
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
            transforming_video = false;
            NET_DVR_StopRealPlay(lRealPlayHandle);
        }
        else if(recv_head_data.dwDataType == heart_test)
        {
            receive_heart_respond = true;
        }
    }
}

int main()
{
    Init();
    run();
    my_exit(SIGINT);
    return 0;
}
