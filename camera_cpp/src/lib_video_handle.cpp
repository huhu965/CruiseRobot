#include "VideoHandle.h"

using namespace std;
using namespace cv;

CameraParam normal_camera;
CameraParam infrared_camera;
VoiceAwakeParam awake_param;

std::map<std::string, create_fun> FunctionMap;

//字符串分割函数
std::vector<std::string> split(std::string str, std::string pattern)
{
    std::string::size_type pos;
    std::vector<std::string> result;
    str += pattern;//扩展字符串以方便操作
    int size = str.size();
    for (int i = 0; i < size; i++)
    {
        pos = str.find(pattern, i);
        if (pos < size)
        {
            std::string s = str.substr(i, pos - i);
            result.push_back(s);
            i = pos + pattern.size() - 1; //for会自动加一
        }
    }
    return result;
}

std::map<std::string, std::string> split_url_param(std::string url_param)
{
    std::map<std::string, std::string> result;
    std::vector<std::string> params = split(url_param, "&");
    for(int i=0,n_size = params.size();i<n_size;i++)
    {
        std::vector<std::string> param = split(params[i], "=");
        result[param[0]] = param[1];
    }
    return result;
}
//图片格式转换
string transform_TYV12_to_CV8UC3(char * pBuf, int nSize, FRAME_INFO * pFrameInfo)
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
    // imshow("IPCamera", pImg);
    // waitKey(1);
    return str_img;
}
//语音唤醒回调函数
int cb_ivw_msg_proc( const char *sessionID, int msg, int param1, int param2, const void *info, void *userData )
{
    VoiceAwakeParamPtr _awake_param_ptr = (VoiceAwakeParam*)userData;
	if (MSP_IVW_MSG_ERROR == msg) //唤醒出错消息
	{
        char sse_hints[128];
        snprintf(sse_hints, sizeof(sse_hints), "QIVWAudioWrite errorCode=%d", param1);
        QIVWSessionEnd(_awake_param_ptr->session_id, sse_hints);
        _awake_param_ptr->session_id = NULL;
	}
	else if (MSP_IVW_MSG_WAKEUP == msg) //唤醒成功消息
	{
        _awake_param_ptr->is_awake = true;
        //向语音识别发送指令，已经被唤醒
        std::string awake_commond = "GET /gs_robot/cmd/voice_awake\r\n";
        int num = sendto(normal_camera.voice_upload_socket, awake_commond.c_str(), awake_commond.length(),
                    0 , (struct sockaddr *)&normal_camera.voice_cmd_addr, sizeof(struct sockaddr));
        //这里没有用锁，有可能数据冲突出错误
    }
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
// 实时流回调
void CALLBACK fRealDataCallBack(LONG lRealHandle, DWORD dwDataType, BYTE *pBuffer, DWORD dwBufSize, void *pUser){
    CameraParamPtr camera_ptr = (CameraParamPtr)pUser;
    HeadData head_data;
    char video_data_Buffer[10000]; //发送缓冲区
    memset(video_data_Buffer, 0, sizeof(video_data_Buffer)); //清空
    head_data.dwDataType = dwDataType;
    head_data.dwBufSize = dwBufSize;
    memcpy(video_data_Buffer, pBuffer, dwBufSize);
    send(camera_ptr->socket_tcp, (char*)&head_data, sizeof(HeadData), MSG_WAITALL);
    send(camera_ptr->socket_tcp, video_data_Buffer, dwBufSize, MSG_WAITALL);//通过tcp直接发送码流
    if(camera_ptr->have_voice == true){
        switch (dwDataType)
        {
            case NET_DVR_SYSHEAD: //系统头
                if (!PlayM4_GetPort(&camera_ptr->nPort)){  //获取播放库未使用的通道号
                    cout<<"获取播放库号失败"<<endl;
                }
                if (!PlayM4_SetStreamOpenMode(camera_ptr->nPort, STREAME_REALTIME)){  //设置实时流播放模式
                    cout<<"设置实时流播放模式失败"<<endl;
                }
                if (!PlayM4_OpenStream(camera_ptr->nPort, pBuffer, dwBufSize, 10 * 1024 * 1024)){ //打开流接口
                    cout<<"打开流接口失败"<<endl;
                }
                if (!PlayM4_SetDecCallBack(camera_ptr->nPort, voice_DecCBFun)){//设置解码回调函数，获取解码后的数据
                    cout<<"设置解码回调函数失败"<<endl;
                }
                if (!PlayM4_Play(camera_ptr->nPort, NULL)){ //播放开始
                    cout<<"播放失败"<<endl;
                }
                //打开音频解码, 需要码流是复合流
                if (!PlayM4_PlaySound(camera_ptr->nPort))
                {
                    cout<<"音频播放失败"<<endl;
                } 
                break;
            case NET_DVR_STREAMDATA:
                //码流数据
                if (dwBufSize > 0 && camera_ptr->nPort != -1)
                {
                    if (!PlayM4_InputData(camera_ptr->nPort, pBuffer, dwBufSize))
                        {
                            cout << "error" << PlayM4_GetLastError(camera_ptr->nPort) << endl;
                            break;
                        }
                }
                break;
            default:
                //其他数据
                if (dwBufSize > 0 && camera_ptr->nPort != -1)
                {
                    if (!PlayM4_InputData(camera_ptr->nPort, pBuffer, dwBufSize))
                    {
                        break;
                    }
                }
                break;
        }
    }
}

void Resample16K(short* pInAudioData, int nInAudioLen, short* pOutAudioData, int& nOutAudioLen)
{//short占两个字节
	short* sSampleIn = pInAudioData;
	int nFrequency = 0;
	while (sSampleIn - pInAudioData < nInAudioLen)
	{
		memcpy((char*)(pOutAudioData + nFrequency), (char*)sSampleIn, 2);
		nFrequency++;
		memcpy((char*)(pOutAudioData + nFrequency), (char*)sSampleIn, 2);
		nFrequency++;
		sSampleIn++;
	}
	//字节长度
	nOutAudioLen = nFrequency*2;
}
//音频为PCM数据
void CALLBACK voice_DecCBFun(int nPort, char * pBuf, int nSize, FRAME_INFO * pFrameInfo, void* nReserved1,int nReserved2)
{
    long lFrameType = pFrameInfo->nType;
    int err_code = MSP_SUCCESS;

    if(lFrameType == T_AUDIO16)
    {
        if(awake_param.is_awake == false){
            char data_Buffer[16000];
            memset(data_Buffer, 0, sizeof(data_Buffer)); //清空
            // memcpy(data_Buffer,pBuf,nSize);
            int out_len = 0;
            //            输入数组      short长度   输出的数组           输出的字节长度
            Resample16K((short*)pBuf ,nSize/2, (short*)data_Buffer, out_len);//8K转为16k
            // cout<<out_len<<endl;
            err_code = QIVWAudioWrite(awake_param.session_id, 
                                    (const void *)data_Buffer, 
                                    out_len, 
                                    awake_param.audio_stat);
            // int num = sendto(normal_camera.voice_upload_socket, data_Buffer, out_len,
            //     0 , (struct sockaddr *)&normal_camera.voice_addr, sizeof(struct sockaddr));
            // cout<<"发送："<<num<<endl;
            if (MSP_SUCCESS != err_code)
            {
                printf("QIVWAudioWrite failed! error code:%d\n",err_code);
                char sse_hints[128];
                snprintf(sse_hints, sizeof(sse_hints), "QIVWAudioWrite errorCode=%d", err_code);
                QIVWSessionEnd(awake_param.session_id, sse_hints);
                awake_param.session_id = NULL;
            }
            // cout<<"ok"<<endl;
            if (MSP_AUDIO_SAMPLE_FIRST == awake_param.audio_stat)
            {
                awake_param.audio_stat = MSP_AUDIO_SAMPLE_CONTINUE;
            }
        }
        else{ //如果唤醒了，就传数据
            // memcpy(data_Buffer,pBuf,nSize);
            // int out_len = 0;
            //            输入数组      short长度   输出的数组           输出的字节长度
            // Resample16K((short*)pBuf ,nSize/2, (short*)data_Buffer, out_len);//8K转为16k
            int num = sendto(normal_camera.voice_upload_socket, pBuf, nSize,
                        0 , (struct sockaddr *)&normal_camera.voice_addr, sizeof(struct sockaddr));
        }
    }
}
// 解码回调 视频为YUV数据(YV12)，音频为PCM数据
void CALLBACK normal_DecCBFun(int nPort, char * pBuf, int nSize, FRAME_INFO * pFrameInfo, void* nReserved1,int nReserved2)
{
    long lFrameType = pFrameInfo->nType;
    if (lFrameType == T_YV12)
    {
        string str_img = transform_TYV12_to_CV8UC3(pBuf,nSize,pFrameInfo);
        int num = sendto(normal_camera.socket_udp, str_img.c_str(), str_img.length(),
                         0 , (struct sockaddr *)&normal_camera.udp_server_addr, sizeof(struct sockaddr));
    }
    else if(lFrameType == T_AUDIO16)
    {
        char data_Buffer[8000];
        memset(data_Buffer, 0, sizeof(data_Buffer)); //清空
        memcpy(data_Buffer,pBuf,nSize);
        int num = sendto(normal_camera.voice_upload_socket, data_Buffer, nSize,
                     0 , (struct sockaddr *)&normal_camera.voice_addr, sizeof(struct sockaddr));
    }
}

void CALLBACK infrared_DecCBFun(int nPort, char * pBuf, int nSize, FRAME_INFO * pFrameInfo, void* nReserved1,int nReserved2)
{
    long lFrameType = pFrameInfo->nType;
    if (lFrameType == T_YV12)
    {
        string str_img = transform_TYV12_to_CV8UC3(pBuf,nSize,pFrameInfo);
        int num = sendto(infrared_camera.socket_udp, str_img.c_str(), str_img.length(),
                         0 , (struct sockaddr *)&infrared_camera.udp_server_addr, sizeof(struct sockaddr));
        // cout<<num<<endl;
    }
}

void CALLBACK RemoteConfigCallback(DWORD dwType, void *lpBuffer, DWORD dwBufLen, void *pUserData)
{
    if (dwType == NET_SDK_CALLBACK_TYPE_DATA)
    {
        LPNET_DVR_THERMOMETRY_UPLOAD lpThermometry = new NET_DVR_THERMOMETRY_UPLOAD;
        memcpy(lpThermometry, lpBuffer, sizeof(*lpThermometry));
        LPNET_DVR_THERMOMETRY_UPLOAD _temperature_ptr = (LPNET_DVR_THERMOMETRY_UPLOAD)lpBuffer;
    
        // if(lpThermometry->byRuleCalibType==0) //点测温
        // {
        //     printf("点测温信息:fTemperature[%f]\n", lpThermometry->struPointThermCfg.fTemperature);
        // } 
 
        if((lpThermometry->byRuleCalibType==1)||(lpThermometry->byRuleCalibType==2)) //框/线测温
        {
            char data_buff[256];
            memset(data_buff, 0, sizeof(data_buff)); //清空
            int data_size = sprintf(data_buff,"max_temperature=%.2f&min_temperature=%.2f&average_temperature=%.2f",
                                    _temperature_ptr->struLinePolygonThermCfg.fMaxTemperature,
                                    _temperature_ptr->struLinePolygonThermCfg.fMinTemperature,
                                    _temperature_ptr->struLinePolygonThermCfg.fAverageTemperature);
            // cout<<data_buff<<endl;              
            int num = sendto(infrared_camera.socket_udp, data_buff, data_size,
                         0 , (struct sockaddr *)&infrared_camera.udp_server_addr, sizeof(struct sockaddr));
        }
 
        if (lpThermometry != NULL)
        {
            delete lpThermometry;
            lpThermometry = NULL;
        }
    }
    else if (dwType == NET_SDK_CALLBACK_TYPE_STATUS)
    {
        DWORD dwStatus = *(DWORD*)lpBuffer;
        if (dwStatus == NET_SDK_CALLBACK_STATUS_SUCCESS)
        {
            printf("dwStatus:NET_SDK_CALLBACK_STATUS_SUCCESS\n");            
        }
        else if (dwStatus == NET_SDK_CALLBACK_STATUS_FAILED)
        {
            DWORD dwErrCode = *(DWORD*)((char *)lpBuffer + 4);
            printf("NET_DVR_GET_MANUALTHERM_INFO failed, Error code %d\n", dwErrCode);
        }
    }
}

/*云台控制*/
void PTZ_control(void* args){
    string _url_param = *(string*)args;
    PTZParam _ptz_param;
    std::map<std::string, std::string> params = split_url_param(_url_param);
    _ptz_param.lUserID = normal_camera.lUserID;
    _ptz_param.dwPTZCommand = atoi(params["dwPTZCommand"].c_str());
    _ptz_param.dwSpeed = atoi(params["dwSpeed"].c_str());
    _ptz_param.dwStop = atoi(params["dwStop"].c_str());
    _PTZ_control(&_ptz_param);
}
void _PTZ_control(void* args){
    PTZParam _ptz_param = *(PTZParamPtr)args;
    NET_DVR_PTZControlWithSpeed_Other(_ptz_param.lUserID,1,_ptz_param.dwPTZCommand,_ptz_param.dwStop,_ptz_param.dwSpeed);
}
/*视频开始传输*/
void video_begin(void* args){
    string _url_param = *(string*)args;
    std::map<std::string, std::string> params = split_url_param(_url_param);
    switch( atoi(params["camera"].c_str()) )
    {
        case 0:
            _video_begin(&normal_camera);
            _video_begin(&infrared_camera);
            break;
        case 1:
            _video_begin(&normal_camera);
            break;
        case 2:
            _video_begin(&infrared_camera);
            break;
        default:
            break;
    }
}
void _read_temperature(void* args)
{
    CameraParamPtr _camera_param_ptr = (CameraParamPtr)args;
    NET_DVR_REALTIME_THERMOMETRY_COND thermometry ={0};
    thermometry.dwSize = sizeof(thermometry);// 结构体大小
    thermometry.byRuleID = 1;// 规则ID
    thermometry.dwChan = 1;// 通道号
    thermometry.wInterval = 3;

    _camera_param_ptr->lTemperatureHandle = NET_DVR_StartRemoteConfig(_camera_param_ptr->lUserID,
                                    NET_DVR_GET_REALTIME_THERMOMETRY,
                                    &thermometry,sizeof(thermometry),RemoteConfigCallback,NULL);
    cout<<"启动:"<<_camera_param_ptr->lTemperatureHandle<<endl;
}
void _video_begin(void* args){
    CameraParamPtr _camera_param_ptr = (CameraParamPtr)args;
    _camera_param_ptr->lRealPlayHandle = NET_DVR_RealPlay_V40(_camera_param_ptr->lUserID, 
                                                        &_camera_param_ptr->struPlayInfo, 
                                                        fRealDataCallBack, 
                                                        _camera_param_ptr);//开始取流解码
    _camera_param_ptr->transforming_video = true;
    if (_camera_param_ptr->lRealPlayHandle < 0){
        _camera_param_ptr->transforming_video = false;
        printf("NET_DVR_RealPlay_V40 error\n");
        printf("%d\n", NET_DVR_GetLastError()); 
    }
}
/*视频暂停传输*/
void video_stop(void* args){
    string _url_param = *(string*)args;
    std::map<std::string, std::string> params = split_url_param(_url_param);
    switch( atoi(params["camera"].c_str()) )
    {
        case 0:
            _video_stop(&normal_camera);
            _video_stop(&infrared_camera);
            break;
        case 1:
            _video_stop(&normal_camera);
            break;
        case 2:
            _video_stop(&infrared_camera);
            break;
        default:
            break;
    }
}
void _video_stop(void* args){
    CameraParamPtr _camera_param_ptr = (CameraParamPtr)args;
    NET_DVR_StopRealPlay(_camera_param_ptr->lRealPlayHandle);
    _camera_param_ptr->transforming_video = false;
}

//链接服务器
void _connect_server(void* args){
    CameraParamPtr _camera_param_ptr = (CameraParamPtr)args;
    while(connect(_camera_param_ptr->socket_tcp, (struct sockaddr *)&_camera_param_ptr->server_addr, sizeof(struct sockaddr)) < 0)
    {
        perror("connect error");
        cout<<"服务器不在线"<<endl;
        sleep(5);
    }
    send(_camera_param_ptr->socket_tcp, _camera_param_ptr->register_identity.c_str(), _camera_param_ptr->register_identity.length(), MSG_WAITALL); //向服务器端注册是机器人
}


//关闭服务器链接
void _disconnect_server(void* args){
    CameraParamPtr _camera_param_ptr = (CameraParamPtr)args;
    close(_camera_param_ptr->socket_tcp);
}

//构建指令接收服务器
void _build_cmd_server(void* args){
    CameraParamPtr _camera_param_ptr = (CameraParamPtr)args;
    unsigned int yes = 1;
    setsockopt(_camera_param_ptr->command_receive_socket, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    //绑定udp接收
    if(bind(_camera_param_ptr->command_receive_socket, (struct sockaddr *)&_camera_param_ptr->command_addr, sizeof(struct sockaddr)) < 0){
        cout<<"server connect error"<<endl;
    }
}

//关闭指令接收服务器
void _close_cmd_server(void* args){
    CameraParamPtr _camera_param_ptr = (CameraParamPtr)args;
    close(_camera_param_ptr->command_receive_socket);
}

//登录摄像头
void _login_camera(void* args){
    CameraParamPtr _camera_param_ptr = (CameraParamPtr)args;
    while(1){
        _camera_param_ptr->lUserID = NET_DVR_Login_V30(_camera_param_ptr->addrcream, 
                                                8000, 
                                                _camera_param_ptr->name, 
                                                _camera_param_ptr->password, 
                                                &_camera_param_ptr->struDeviceInfo);//登录摄像头
        if (_camera_param_ptr->lUserID < 0){
            printf("Login error, %d\n", NET_DVR_GetLastError());
            sleep(10);
        }
        else{
            break;
        }
    }
}

void voice_sleep(void* args)
{
    _voice_sleep(&awake_param);
}
//语音系统休眠，恢复标志位
void _voice_sleep(void* args)
{
    VoiceAwakeParamPtr _awake_param_ptr = (VoiceAwakeParam*)args;
    QIVWSessionEnd(_awake_param_ptr->session_id,"ok");
    _awake_param_ptr->is_awake = false;
    _awake_param_ptr->session_id = NULL;
    _awake_param_ptr->audio_stat = MSP_AUDIO_SAMPLE_FIRST;
}