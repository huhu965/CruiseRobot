#include "VideoHandle.h"
using namespace std;
using namespace cv;

pthread_t video_handle_thread;
pthread_t infrared_video_handle_thread;

void *video_handle_func(void* args){
    CameraParamPtr _camera_param_ptr = (CameraParam*)args;
    HeadData _recv_head;
    unsigned char recv_buf[25600];

    _connect_server(_camera_param_ptr); //链接服务器
    sleep(2);
    //告诉机器人开始
    HeadData headdata;
    headdata.dwDataType = begin_trans;  
    headdata.dwBufSize = 0;
    send(_camera_param_ptr->socket_tcp, (char*)&headdata, sizeof(HeadData),MSG_WAITALL);

    while(true){
        memset(&_recv_head, 0, sizeof(HeadData)); //清空
        int recv_len = recv(_camera_param_ptr->socket_tcp, (char*)&_recv_head, sizeof(HeadData), MSG_WAITALL);

        memset(recv_buf, 0, sizeof(recv_buf)); //清空
        int recv_num = recv(_camera_param_ptr->socket_tcp, recv_buf, _recv_head.dwBufSize, MSG_WAITALL);
        if(recv_num == 0){
            cout<<"error"<<endl;
            exit(0);
        }
        if(_recv_head.dwDataType == 1){
            recv_buf[recv_num] = '\0';
            if (!PlayM4_GetPort(&_camera_param_ptr->nPort)){  //获取播放库未使用的通道号
                cout<<"获取播放库号失败"<<endl;
            }
            // cout<<_camera_param_ptr->nPort<<endl;
            if (!PlayM4_SetStreamOpenMode(_camera_param_ptr->nPort, STREAME_REALTIME)){  //设置实时流播放模式
                cout<<"设置实时流播放模式失败"<<endl;
            }
            if (!PlayM4_OpenStream(_camera_param_ptr->nPort, recv_buf, recv_num, 10 * 1024 * 1024)){ //打开流接口
                cout<<"打开流接口失败"<<endl;
            }

            if(_camera_param_ptr->have_voice){
                if (!PlayM4_SetDecCallBack(_camera_param_ptr->nPort, normal_DecCBFun)){//设置解码回调函数，获取解码后的数据
                    cout<<"设置解码回调函数失败"<<endl;
                }
                // cout<<"normal_DecCBFun"<<endl;
            }
            else{
                if (!PlayM4_SetDecCallBack(_camera_param_ptr->nPort, infrared_DecCBFun)){//设置解码回调函数，获取解码后的数据
                    cout<<"设置解码回调函数失败"<<endl;
                }
                // cout<<"infrared_DecCBFun"<<endl;
            }

            if (!PlayM4_Play(_camera_param_ptr->nPort, NULL)){ //播放开始
                cout<<"播放失败"<<endl;
            }
            if(_camera_param_ptr->have_voice){
                //打开音频解码, 需要码流是复合流
                if (!PlayM4_PlaySound(_camera_param_ptr->nPort)){
                    cout<<"音频播放失败"<<endl;
                }
            }
        }
        else if(_recv_head.dwDataType == 2)
        {
            if (!PlayM4_InputData(_camera_param_ptr->nPort, recv_buf, recv_num))
            {
                cout << "error" << PlayM4_GetLastError(_camera_param_ptr->nPort) << endl;
            }
        }
    }
    pthread_exit(NULL);
}

void exit_func(int sig)
{   
    HeadData headdata;
    headdata.dwDataType = end_trans;  //告诉机器人结束
    headdata.dwBufSize = 0;
    cout<<normal_camera.socket_tcp<<endl;
    cout<<infrared_camera.socket_tcp<<endl;
    send(normal_camera.socket_tcp, (char*)&headdata, sizeof(HeadData),0);
    send(infrared_camera.socket_tcp, (char*)&headdata, sizeof(HeadData),0);

    cout<<"EXIT"<<endl;
    sleep(5);
    _disconnect_server(&normal_camera);
    _disconnect_server(&infrared_camera);
    exit(sig);
}

void param_init(){
    struct sockaddr_in addr;
    //清空
    memset(&normal_camera, 0, sizeof(CameraParam));
    memset(&infrared_camera, 0, sizeof(CameraParam)); 
    //设置服务器地址
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(62222);//将一个无符号短整型的主机数值转换为网络字节顺序，即大尾顺序(big-endian)
    addr.sin_addr.s_addr = inet_addr("101.37.16.240");
    // addr.sin_addr.s_addr = inet_addr("10.7.5.127");

    normal_camera.server_addr = addr;
    infrared_camera.server_addr = addr;
    //红外视频
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8003);
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    infrared_camera.udp_server_addr = addr;

    //正常视频
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8000);//指令接收端口
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    normal_camera.udp_server_addr = addr;
    //音频
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8001);
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    normal_camera.voice_addr = addr;

    normal_camera.register_identity = "soft_video \r\n";
    normal_camera.socket_tcp = socket(AF_INET, SOCK_STREAM, 0);
    normal_camera.socket_udp = socket(AF_INET, SOCK_DGRAM, 0);
    normal_camera.voice_upload_socket = socket(AF_INET, SOCK_DGRAM, 0);
    
    infrared_camera.register_identity = "soft_video_red \r\n";
    infrared_camera.socket_tcp = socket(AF_INET, SOCK_STREAM, 0);
    infrared_camera.socket_udp = socket(AF_INET, SOCK_DGRAM, 0);
    normal_camera.have_voice = true;
    infrared_camera.have_voice = false;
}

void Init(){
    signal(SIGINT, exit_func); // 设置信号
    param_init();
    int rc1 = pthread_create(&video_handle_thread, NULL, video_handle_func,&normal_camera);//创建接收命令线程
    if (rc1){
        cout << "Error:无法创建线程:" << rc1 << endl;
    }
    int rc2 = pthread_create(&infrared_video_handle_thread, NULL, video_handle_func,&infrared_camera);//创建接收命令线程
    if (rc2){
        cout << "Error:无法创建线程:" << rc2 << endl;
    }
}

int main()
{
    Init();
    while(true)
    {
        sleep(1);
    }
}