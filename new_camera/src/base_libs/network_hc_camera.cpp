/* 
 * @Author: Hu Ziwei
 * @Description: 
 * @Date: 2021-07-15 20:02:25
 * @Last Modified by: Hu Ziwei
 * @Last Modified time: 2021-07-16 00:40:08
 * @命名规则
 *   1.类名和方法命名用驼峰，FunName
 *   2.类内变量，全部小写，下划线分割，param_name
 *   3.类内私有的变量和方法统一在最后加下划线，FunNam_;param_name_
 *   4.函数内临时变量统一在前面加下划线，_param_name
 *   5.方法名带数字驼峰不好阅读时，加_下划线分割，Transform_Tyv12_To_Cv8uc3
*/

#include "robot_background/network_hc_camera.hpp"
#include "robot_background/base_func.hpp"

namespace robot_background{
NetworkHcCameraHandle::NetworkHcCameraHandle(CameraParam camera_param, 
                                            NetworkSocketParam network_socket_param,
                                            std::string register_identity,
                                            int data_store_max_number
                                            )
                                            :HcCameraHandle(camera_param), 
                                            network_socket_param_(network_socket_param), 
                                            data_buff_size_(0),
                                            data_stamp_(0), 
                                            data_store_max_number_(data_store_max_number), 
                                            data_store_number_(0),
                                            register_identity_(register_identity){
    memset(&data_buff_, 0, sizeof(data_buff_));
    LogIn();
}
/*
    * @Description:打开读取温度
*/
void NetworkHcCameraHandle::ReadTemperature(){
    NET_DVR_REALTIME_THERMOMETRY_COND _thermometry ={0};
    _thermometry.dwSize = sizeof(_thermometry);// 结构体大小
    _thermometry.byRuleID = 1;// 规则ID
    _thermometry.dwChan = 1;// 通道号
    _thermometry.wInterval = 3;//读取间隔三秒，但感觉没什么区别，有空再测试
    camera_param.lTemperatureHandle = NET_DVR_StartRemoteConfig(camera_param.lUserID,
                                                                NET_DVR_GET_REALTIME_THERMOMETRY,
                                                                &_thermometry, 
                                                                sizeof(_thermometry), 
                                                                NetworkHcCameraHandle::RemoteConfigCallback, //回调函数
                                                                this);
    if(camera_param.lTemperatureHandle < 0){
        std::cout<<"温度读取失败，错误值："<<NET_DVR_GetLastError()<<std::endl;
    }else{
        std::cout<<"温度读取成功，返回值："<<camera_param.lTemperatureHandle<<std::endl;
    }
}

/*
    * @Description:打开视频实时预览
*/
void NetworkHcCameraHandle::VideoBegin(){
    camera_param.lRealPlayHandle = NET_DVR_RealPlay_V40(camera_param.lUserID, 
                                                &camera_param.struPlayInfo, 
                                                NetworkHcCameraHandle::fRealDataCallBack,
                                                this);//开始取流解码
    if(camera_param.lRealPlayHandle < 0){
        std::cout<<"预览播放失败，错误值："<<NET_DVR_GetLastError()<<std::endl;
    }else{
        std::cout<<"预览播放成功，返回值："<<camera_param.lRealPlayHandle<<std::endl;
    }
}
/*
    * @Description:打开声音获取
*/
void NetworkHcCameraHandle::ReadVoice(){
    camera_param.lVoiceHanle = NET_DVR_StartVoiceCom_V30(camera_param.lUserID, 1,AUDIO_DATA_TYPE, NetworkHcCameraHandle::fVoiceDataCallBack, this);
    if(camera_param.lVoiceHanle < 0){
        std::cout<<"声音读取失败，错误值："<<NET_DVR_GetLastError()<<std::endl;
    }else{
        std::cout<<"声音读取成功，返回值："<<camera_param.lVoiceHanle<<std::endl;
    }
}
/*
    * @Description:链接服务器
*/
void NetworkHcCameraHandle::ConnectVideoServer(){
    while(connect(network_socket_param_.tcp_video_socket, 
                (struct sockaddr *)&network_socket_param_.tcp_video_server_addr
                , sizeof(struct sockaddr)) < 0){
        perror("connect error");
        std::cout<<register_identity_<<" 服务器不在线"<<std::endl;
        sleep(5);
    }
    send(network_socket_param_.tcp_video_socket, 
        register_identity_.c_str(), 
        register_identity_.length(), 
        MSG_WAITALL); //向服务器端注册是机器人
}
/*
    * @Description:断开链接服务器
*/
void NetworkHcCameraHandle::DisconnectVideoServer(){
    close(network_socket_param_.tcp_video_socket);
}

void NetworkHcCameraHandle::VideoCmdHandle(){
    HeadData _recv_head;
    while(true){
        memset(&_recv_head, 0, sizeof(HeadData)); //清空
        recv(network_socket_param_.tcp_video_socket, (char*)&_recv_head, sizeof(HeadData), MSG_WAITALL);

        if(_recv_head.dwDataType == begin_trans)
        {
            std::cout<<"begin"<<std::endl;
            VideoBegin();
        }
        else if(_recv_head.dwDataType == end_trans)
        {
            std::cout<<"end"<<std::endl;
            VideoStop();
        }
    }

}
/*
    * @Description:温度数据回调函数
*/
void CALLBACK NetworkHcCameraHandle::RemoteConfigCallback(DWORD dwType, void *lpBuffer, DWORD dwBufLen, void *pUserData){ 
    NetworkHcCameraHandle *_ptr = (NetworkHcCameraHandle *)pUserData;
    if (dwType == NET_SDK_CALLBACK_TYPE_DATA){
        LPNET_DVR_THERMOMETRY_UPLOAD _temperature_ptr = (LPNET_DVR_THERMOMETRY_UPLOAD)lpBuffer;
 
        if((_temperature_ptr->byRuleCalibType==1)||(_temperature_ptr->byRuleCalibType==2)){  //框/线测温
            char data_buff[256];
            memset(data_buff, 0, sizeof(data_buff)); //清空
            int data_size = sprintf(data_buff,"max_temperature=%.2f&min_temperature=%.2f&average_temperature=%.2f",
                                    _temperature_ptr->struLinePolygonThermCfg.fMaxTemperature,
                                    _temperature_ptr->struLinePolygonThermCfg.fMinTemperature,
                                    _temperature_ptr->struLinePolygonThermCfg.fAverageTemperature);

            int num = sendto(_ptr->network_socket_param_.udp_client_socket, 
                            data_buff, data_size,
                            0 , 
                            (struct sockaddr *)&_ptr->network_socket_param_.udp_server_addr, 
                            sizeof(struct sockaddr));
        }
    }
}

/*
    * @Description:音频回调函数
*/
void CALLBACK NetworkHcCameraHandle::fVoiceDataCallBack(LONG lVoiceComHandle, 
                                                        char *pRecvDataBuffer, 
                                                        DWORD dwBufSize, 
                                                        BYTE byAudioFlag, 
                                                        void*pUser){
    NetworkHcCameraHandle *_ptr = (NetworkHcCameraHandle *)pUser;
    std::cout<<"音频回调函数"<<std::endl;
    //byAudioFlag 1是设备发过来的数据，0是本地采集数据
    if(byAudioFlag == 1){
        //            输入数组      short长度   输出的数组           输出的字节长度
        // Resample16K((short*)pBuf ,nSize/2, (short*)data_Buffer, out_len);//8K转为16k
        std::cout<<"音频数据大小:"<<dwBufSize<<std::endl;
        int num = sendto(_ptr->network_socket_param_.udp_client_socket, 
                        pRecvDataBuffer, 
                        dwBufSize,
                        0 , 
                        (struct sockaddr *)&_ptr->network_socket_param_.udp_server_addr, 
                        sizeof(struct sockaddr));
    } 
}
/*
    * @Description:视频回调函数
*/
void CALLBACK NetworkHcCameraHandle::fRealDataCallBack(LONG lRealHandle, 
                                                    DWORD dwDataType, 
                                                    BYTE *pBuffer, 
                                                    DWORD dwBufSize, 
                                                    void *pUser){
    NetworkHcCameraHandle *_ptr = (NetworkHcCameraHandle *)pUser;
    HeadData head_data;
    head_data.dwDataType = dwDataType;
    head_data.dwBufSize = dwBufSize;
    
    if(dwDataType == NET_DVR_SYSHEAD)//系统头通过tcp发送
    {
        send(_ptr->network_socket_param_.tcp_video_socket, (char*)&head_data, sizeof(HeadData), MSG_WAITALL);
        send(_ptr->network_socket_param_.tcp_video_socket, (char*)pBuffer, dwBufSize, MSG_WAITALL);//通过tcp直接发送码流
        memset(_ptr->data_buff_, 0, sizeof(_ptr->data_buff_)); //清空

        memcpy(_ptr->data_buff_, (char*)&_ptr->data_stamp_, 4);
        _ptr->data_buff_size_ = 4;
        _ptr->data_stamp_ ++; //时间戳，用于标记顺序
    }
    else{
        // cout<<dwBufSize<<endl;
        if(_ptr->data_store_number_ > _ptr->data_store_max_number_) //如果接收到新的一个I帧，就把之前存的发出去
        {
            // cout<<"发送视频信息："<<camera_ptr->data_stamp<<"  "<<camera_ptr->data_buff_size<<"  "<<camera_ptr->data_store_number<<endl;
            sendto(_ptr->network_socket_param_.udp_video_socket, _ptr->data_buff_, _ptr->data_buff_size_,
            0 , (struct sockaddr *)&_ptr->network_socket_param_.udp_video_server_addr, sizeof(struct sockaddr));
            memset(_ptr->data_buff_, 0, sizeof(_ptr->data_buff_)); //清空

            memcpy(_ptr->data_buff_, (char*)&_ptr->data_stamp_, 4);
            memcpy(_ptr->data_buff_+4, pBuffer, dwBufSize);
            _ptr->data_buff_size_ = dwBufSize + 4;
            _ptr->data_stamp_ ++; //时间戳，用于标记顺序
            _ptr->data_store_number_ = 1;
        }else{
            memcpy(_ptr->data_buff_ + _ptr->data_buff_size_, pBuffer, dwBufSize);
            _ptr->data_buff_size_ += dwBufSize;
            _ptr->data_store_number_ ++;
        }
    }
}

/*
    * @Description:构建指令接收服务器
*/
void NetworkHcCameraHandle::BuildCmdServer(){
    unsigned int _yes = 1;
    // 设置超时
    struct timeval _timeout;
    _timeout.tv_sec = 2;//秒
    _timeout.tv_usec = 0;//微秒
    setsockopt(network_socket_param_.udp_command_socket, SOL_SOCKET, SO_RCVTIMEO, &_timeout, sizeof(_timeout));
    setsockopt(network_socket_param_.udp_command_socket, SOL_SOCKET, SO_REUSEADDR, &_yes, sizeof(_yes));
    //绑定udp接收
    if(bind(network_socket_param_.udp_command_socket, 
            (struct sockaddr *)&network_socket_param_.udp_command_addr, 
            sizeof(struct sockaddr)) < 0){
        std::cout<<"指令接收通道构建失败"<<std::endl;
    }
}
/*
    * @Description:处理接收到的指令
*/
void NetworkHcCameraHandle::CmdHandle(){
    char _recv_Buf[512];
    std::string _url_cmd, _url_param;
    memset(_recv_Buf, 0, sizeof(_recv_Buf)); //清空
    int recv_num = recvfrom(network_socket_param_.udp_command_socket, 
                            _recv_Buf, sizeof(_recv_Buf), 0, 
                            (struct sockaddr *)&network_socket_param_.udp_command_addr, 
                            (socklen_t *)sizeof(struct sockaddr));
    //处理命令
    std::string _url = _recv_Buf;
    std::string::size_type pos = _url.find("?");
    if(pos!=std::string::npos){//还有参数
        std::vector<std::string> result=Split(_url,"?");
        _url_cmd = result[0];
        _url_param = result[1];
    }
    else{
        _url_cmd = _url;
        _url_param = "";
    }
    if(_url_cmd == "ptz_control"){
        PTZControl(&_url_param);
    }
}

}