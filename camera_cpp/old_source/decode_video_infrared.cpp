#include <stdio.h>
#include <stdlib.h>
#include <cstdlib>
#include <iostream>
#include <cstring>
#include "alsa/asoundlib.h" 
#include "HCNetSDK.h"
#include "LinuxPlayM4.h"
#include <time.h>
#include <opencv2/opencv.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui_c.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <signal.h>
using namespace std;
using namespace cv;

#define begin_trans 22
#define end_trans 23

int socket_fd = socket(AF_INET, SOCK_DGRAM, 0);  //udp通信
struct sockaddr_in addr_host; //把解码后的数据发给后台软件

int socket_rece = socket(AF_INET, SOCK_STREAM, 0); 
struct sockaddr_in addr; //从服务器接收视频数据

struct Data {
  unsigned int dwDataType;
  unsigned int dwBufSize;
 }headdata;

char data_Buffer[10000]; //发送缓冲区


// 解码回调 视频为YUV数据(YV12)，音频为PCM数据
void CALLBACK DecCBFun(int nPort, char * pBuf, int nSize, FRAME_INFO * pFrameInfo, void* nReserved1,int nReserved2)
{
    long lFrameType = pFrameInfo->nType;
    if (lFrameType == T_YV12)
    {
        Mat pImg(pFrameInfo->nHeight, pFrameInfo->nWidth, CV_8UC3);
        Mat src(pFrameInfo->nHeight + pFrameInfo->nHeight / 2, pFrameInfo->nWidth, CV_8UC1, pBuf);

        cvtColor(src, pImg, CV_YUV2BGR_YV12);//转为bgr格式

        vector<uchar> im_buf;
        vector<int> param;
        param.push_back(IMWRITE_JPEG_QUALITY);
        param.push_back(80);//解码后图片的压缩质量，数越大质量越高，数据量越大

        cv::imencode(".jpg", pImg, im_buf,param);
        std::string str_img(im_buf.begin(), im_buf.end());
        int num = sendto(socket_fd, str_img.c_str(), str_img.length(), 0 , (struct sockaddr *)&addr_host, sizeof(struct sockaddr));
        // cout<<num<<endl;
        imshow("IPCamera", pImg);
        waitKey(1);
    }
}

void video_decode_exit(int sig)
{
    headdata.dwDataType = 23;  //告诉机器人结束
    headdata.dwBufSize = 0;
    if(send(socket_rece, (char*)&headdata, sizeof(struct Data),0) < 0)
        perror("connect error");
    cout<<"EXIT"<<endl;
    sleep(5);
    close(socket_rece);
    exit(sig);
}

int main()
{
    long recv_num;  
    int recv_len;
    unsigned char recv_buf[25600];
    LONG nPort = -1;

    memset(&addr, 0, sizeof(addr)); 
    addr.sin_family = AF_INET;
    addr.sin_port = htons(62222);//将一个无符号短整型的主机数值转换为网络字节顺序，即大尾顺序(big-endian)
    addr.sin_addr.s_addr = inet_addr("101.37.16.240");
    //视频
    addr_host.sin_port = htons(8003);//将一个无符号短整型的主机数值转换为网络字节顺序，即大尾顺序(big-endian)
    addr_host.sin_addr.s_addr = inet_addr("127.0.0.1");

    signal(SIGINT, video_decode_exit); // 设置信号

    while(connect(socket_rece, (struct sockaddr *)&addr, sizeof(struct sockaddr)) < 0)
    {
        perror("connect error");
        cout<<"服务器不在线"<<endl;
        sleep(5);
    }

    // headdata.dwDataType = 25;  //25表示解码端
    // headdata.dwBufSize = 0;
    // send(socket_rece, (char*)&headdata, sizeof(struct Data), MSG_WAITALL);
    string register_identity = "soft_video_red \r\n";
    send(socket_rece, register_identity.c_str(), register_identity.length(), MSG_WAITALL); //向服务器端注册是机器人

    headdata.dwDataType = 22;  //告诉机器人开始传输视频
    headdata.dwBufSize = 0;
    send(socket_rece, (char*)&headdata, sizeof(struct Data), MSG_WAITALL);


    while(true)
    {
        memset(&headdata, 0, sizeof(struct Data)); //清空
        recv_len = recv(socket_rece, (char*)&headdata, sizeof(struct Data), MSG_WAITALL);
        memset(recv_buf, 0, sizeof(recv_buf)); //清空
        recv_num = recv(socket_rece, recv_buf, headdata.dwBufSize, MSG_WAITALL);
        // cout<<recv_num<<endl;
        if(recv_num == 0){
            cout<<"error"<<endl;
            exit(0);
        }

        if(headdata.dwDataType == 1){
            recv_buf[recv_num] = '\0';
            // cout<<recv_buf<<endl;
            if (!PlayM4_GetPort(&nPort)){  //获取播放库未使用的通道号
                cout<<"获取播放库号失败"<<endl;
            }
            if (!PlayM4_SetStreamOpenMode(nPort, STREAME_REALTIME)){  //设置实时流播放模式
                cout<<"设置实时流播放模式失败"<<endl;
            }
            if (!PlayM4_OpenStream(nPort, recv_buf, recv_num, 10 * 1024 * 1024)){ //打开流接口
                cout<<"打开流接口失败"<<endl;
            }
            if (!PlayM4_SetDecCallBack(nPort, DecCBFun)){//设置解码回调函数，获取解码后的数据
                cout<<"设置解码回调函数失败"<<endl;
            }
            if (!PlayM4_Play(nPort, NULL)){ //播放开始
                cout<<"播放失败"<<endl;
            } 
        }
        else if(headdata.dwDataType == 2)
        {
            if (!PlayM4_InputData(nPort, recv_buf, recv_num))
            {
                cout << "error" << PlayM4_GetLastError(nPort) << endl;
                break;
            }
        }
    }
}