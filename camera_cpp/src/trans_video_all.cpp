/*
 * @Description:{} 
 * @Author: Hu Ziwei  
 * @Date: 2021-07-06 23:39:48  
 * @Last Modified by: Hu Ziwei
 * @Last Modified time: 2021-07-06 23:43:17
*/


#include "VideoHandle.h"
using namespace std;

int test;
extern CameraParam normal_camera;
extern CameraParam infrared_camera;
pthread_t cmd_recv_thread;
//心跳发送线程
pthread_t heart_send_thread1;
//心跳发送线程
pthread_t heart_send_thread2;
pthread_t video_handle_thread;
pthread_t voice_awake_thread;
pthread_t infrared_video_handle_thread;

void FunctionRegister()
{
    FunctionMap["video_begin"] = video_begin;
    FunctionMap["video_stop"] = video_stop;
    FunctionMap["ptz_control"] = PTZ_control;
    FunctionMap["voice_sleep"] = voice_sleep;
}
//退出收尾函数
void exit_func(int sig){
    _video_stop(&normal_camera);
    _video_stop(&infrared_camera);
    _disconnect_server(&normal_camera);
    _disconnect_server(&infrared_camera);
    close(normal_camera.command_receive_socket);
    //注销用户
    NET_DVR_StopRemoteConfig(infrared_camera.lTemperatureHandle);
    NET_DVR_Logout(normal_camera.lUserID);
    NET_DVR_Logout(infrared_camera.lUserID);
    QIVWSessionEnd(awake_param.session_id, "close");
    MSPLogout();
    //释放SDK资源
    NET_DVR_Cleanup();
    exit(sig);
}
void* voice_awake(void* args)
{
    VoiceAwakeParamPtr _awake_param_ptr = (VoiceAwakeParam*)args;
    int ret = MSP_SUCCESS;
    //登录
    ret = MSPLogin(NULL, NULL, _awake_param_ptr->login_param);
    if (MSP_SUCCESS != ret){
        printf("MSPLogin failed, error code: %d.\n", ret);
        MSPLogout(); //退出登录
    }

    while (true){ //循环开启唤醒检测
        int err_code = MSP_SUCCESS;
        char sse_hints[128];
        //初始化唤醒
        // cout<<"唤醒检测"<<endl;
        _awake_param_ptr->session_id=QIVWSessionBegin(_awake_param_ptr->grammar_list, 
                                                    _awake_param_ptr->session_begin_params, 
                                                    &err_code);
        if (err_code != MSP_SUCCESS){
            printf("QIVWSessionBegin failed! error code:%d\n",err_code);
            QIVWSessionEnd(_awake_param_ptr->session_id, "begin error");
            _awake_param_ptr->session_id = NULL;
            sleep(1);
            continue;
        }
        //注册回调函数
        err_code = QIVWRegisterNotify(_awake_param_ptr->session_id, cb_ivw_msg_proc,_awake_param_ptr);
        if (err_code != MSP_SUCCESS){
            snprintf(sse_hints, sizeof(sse_hints), "QIVWRegisterNotify errorCode=%d", err_code);
            printf("QIVWRegisterNotify failed! error code:%d\n",err_code);
            QIVWSessionEnd(_awake_param_ptr->session_id, sse_hints); //释放资源
            _awake_param_ptr->session_id = NULL;
            sleep(1);
            continue;
        }
        while (true){
            if (_awake_param_ptr->session_id == NULL && _awake_param_ptr->is_awake == false){
                _voice_sleep(_awake_param_ptr);
                cout<<"睡眠"<<endl;
                break;
            }
            else{
                sleep(1);
            }
        }  
    }
}

//摄像头传输
void *video_handle_func(void* args){
    CameraParamPtr _camera_param_ptr = (CameraParam*)args;
    HeadData _recv_head;
    NET_DVR_STD_ABILITY ablityparam = {0};
    ablityparam.lpCondBuffer = NULL;
    ablityparam.lpStatusBuffer =(char*)"ThermalCap";

    _connect_server(_camera_param_ptr); //链接服务器
    _login_camera(_camera_param_ptr); //登录摄像头
    if(!_camera_param_ptr->have_voice){
        _read_temperature(_camera_param_ptr);
    }
    _video_begin(_camera_param_ptr);
    while(true){
        memset(&_recv_head, 0, sizeof(HeadData)); //清空
        recv(_camera_param_ptr->socket_tcp, (char*)&_recv_head, sizeof(HeadData), MSG_WAITALL);
        if(_recv_head.dwDataType == heart_test)
        {
            cout<<"xintiao "<<endl;
            _camera_param_ptr->heart_respond = true;
        }
        else if(_recv_head.dwDataType == begin_trans)
        {
            cout<<"begin"<<endl;
            _video_begin(_camera_param_ptr);
        }
        else if(_recv_head.dwDataType == end_trans)
        {
            cout<<"end"<<endl;
            _video_stop(_camera_param_ptr);
        }
    }
    pthread_exit(NULL);
}
//心跳线程
void *heart_func(void* args){
    CameraParamPtr _camera_param_ptr = (CameraParam*)args;
    HeadData _recv_head;
    while (true)
    {
        if(_camera_param_ptr->transforming_video == false)
        {
            memset(&_recv_head, 0, sizeof(HeadData)); //清空
            _recv_head.dwDataType = 24;
            _recv_head.dwBufSize = 0;
            send(_camera_param_ptr->socket_tcp, (char*)&_recv_head, sizeof(HeadData), MSG_WAITALL);
            _camera_param_ptr->heart_respond = false;
        }
        sleep(10);
        if(_camera_param_ptr->heart_respond == false)
        {
            cout<<"链接断开"<<endl;
            _video_stop(_camera_param_ptr);
            _disconnect_server(_camera_param_ptr);
            sleep(10);
            _connect_server(_camera_param_ptr); //链接服务器
            _video_begin(_camera_param_ptr);
        }
    }
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
    addr.sin_addr.s_addr = inet_addr("47.97.11.25");
    // addr.sin_addr.s_addr = inet_addr("10.7.5.127");

    normal_camera.server_addr = addr;
    infrared_camera.server_addr = addr;
    //设置视频udp地址
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(62220);//将一个无符号短整型的主机数值转换为网络字节顺序，即大尾顺序(big-endian)
    addr.sin_addr.s_addr = inet_addr("47.97.11.25");
    normal_camera.video_udp_addr = addr;

    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(62221);//将一个无符号短整型的主机数值转换为网络字节顺序，即大尾顺序(big-endian)
    addr.sin_addr.s_addr = inet_addr("47.97.11.25");
    infrared_camera.video_udp_addr = addr;
    //设置指令接收地址
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8002);//将一个无符号短整型的主机数值转换为网络字节顺序，即大尾顺序(big-endian)
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    normal_camera.command_addr = addr;
    //音频唤醒后发送指令
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8020);
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    normal_camera.voice_cmd_addr = addr;
    //音频传输
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8021);
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    normal_camera.voice_addr = addr;
    //温度传输
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8022);
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    infrared_camera.udp_server_addr = addr;
    //登录结构体初始化
    NET_DVR_PREVIEWINFO struPlayInfo = {0};
    struPlayInfo.hPlayWnd = NULL;         //需要SDK解码时句柄设为有效值，仅取流不解码时可设为空
    struPlayInfo.lChannel = 1;           //预览通道号
    struPlayInfo.dwStreamType = 1;       //0-主码流，1-子码流，2-码流3，3-码流4，以此类推
    struPlayInfo.dwLinkMode = 1;         //0- TCP方式，1- UDP方式，2- 多播方式，3- RTP方式，4-RTP/RTSP，5-RSTP/HTTP
    struPlayInfo.bBlocked = 0; //0- 非阻塞取流， 1- 阻塞取流

    normal_camera.struPlayInfo = struPlayInfo;
    infrared_camera.struPlayInfo = struPlayInfo;
    //设置摄像头登录地址
    normal_camera.addrcream = (char*)"10.7.5.121";
    normal_camera.name = (char*)"admin";
    normal_camera.password = (char*)"sgkj123456";
    normal_camera.transforming_video = false;
    normal_camera.heart_respond = false;
    normal_camera.register_identity = "robot_video \r\n";
    normal_camera.command_receive_socket = socket(AF_INET, SOCK_DGRAM, 0);
    normal_camera.socket_tcp = socket(AF_INET, SOCK_STREAM, 0);
    normal_camera.voice_upload_socket = socket(AF_INET, SOCK_DGRAM, 0);
    normal_camera.video_udp_socket = socket(AF_INET, SOCK_DGRAM, 0);
    normal_camera.have_voice = true;
    normal_camera.data_buff_size = 0;
    normal_camera.data_stamp =0; //时间戳，用于标记顺序
    normal_camera.data_store_max_number = 4;
    normal_camera.data_store_number = 0;

    infrared_camera.addrcream = (char*)"10.7.5.122";
    infrared_camera.name = (char*)"admin";
    infrared_camera.password = (char*)"sgkj123456";
    infrared_camera.register_identity = "robot_video_red \r\n";
    infrared_camera.transforming_video = false;
    infrared_camera.heart_respond = false;
    infrared_camera.socket_tcp = socket(AF_INET, SOCK_STREAM, 0);
    infrared_camera.socket_udp = socket(AF_INET, SOCK_DGRAM, 0);
    infrared_camera.video_udp_socket = socket(AF_INET, SOCK_DGRAM, 0);
    infrared_camera.have_voice = false;
    infrared_camera.data_buff_size = 0;
    infrared_camera.data_stamp =0; //时间戳，用于标记顺序
    infrared_camera.data_store_max_number = 2;
    infrared_camera.data_store_number = 0;

    // awake_param.grammar_list = NULL;
    // awake_param.login_param = "appid = 35dcd3b2,work_dir = .";
    // awake_param.session_begin_params = "ivw_threshold=0:500,sst=wakeup,ivw_res_path =fo|res/ivw/wakeupresource.jet";
    // awake_param.session_id = NULL;
    // awake_param.audio_stat = MSP_AUDIO_SAMPLE_FIRST;
    // awake_param.is_awake = false;
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

    signal(SIGINT, exit_func); // 设置信号

    param_init();
    _build_cmd_server(&normal_camera);
    FunctionRegister(); //注册函数
    int rc1 = pthread_create(&video_handle_thread, NULL, video_handle_func,&normal_camera);//创建接收命令线程
    if (rc1){
        cout << "Error:无法创建线程:" << rc1 << endl;
    }
    int rc2 = pthread_create(&infrared_video_handle_thread, NULL, video_handle_func,&infrared_camera);//创建接收命令线程
    if (rc2){
        cout << "Error:无法创建线程:" << rc2 << endl;
    }

    // int rc3 = pthread_create(&voice_awake_thread, NULL, voice_awake,&awake_param);//创建接收命令线程
    // if (rc3){
    //     cout << "Error:无法创建线程:" << rc3 << endl;
    // }
}

void run(){
    int _socket = normal_camera.command_receive_socket;
    struct sockaddr_in _addr = normal_camera.command_addr;
    char _recv_Buf[512];
    string url_cmd;
    string url_param;
    while(true){
        memset(_recv_Buf, 0, sizeof(_recv_Buf)); //清空
        int recv_num = recvfrom(_socket, _recv_Buf, sizeof(_recv_Buf), 0, (struct sockaddr *)&_addr,(socklen_t *)sizeof(struct sockaddr));
        //处理命令
        string url = _recv_Buf;
        string::size_type pos = url.find("?");
        if(pos!=string::npos){//还有参数
            std::vector<std::string> result=split(url,"?");
            url_cmd = result[0];
            url_param = result[1];
        }
        else{
            url_cmd = url;
            url_param = "";
        }
        create_fun func = FunctionMap.find(url_cmd)->second;  //映射函数
        func(&url_param);
    }
}

int main()
{
    Init();
    run();
    exit_func(SIGINT);
    return 0;
}
