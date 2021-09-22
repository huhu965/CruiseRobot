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

#include "robot_background/hc_camera.hpp"

namespace robot_background{
    HcCameraHandle::HcCameraHandle(CameraParam camera_param):camera_param(camera_param){}
    /*
        * @Description:登录摄像头
    */
    void HcCameraHandle::LogIn(){
        camera_param.lUserID = NET_DVR_Login_V30(camera_param.addr_camera, 
                                                8000, 
                                                camera_param.name, 
                                                camera_param.password, 
                                                &camera_param.struDeviceInfo);//登录摄像头
        if (camera_param.lUserID < 0){
            std::cout<<"Login error: "<< NET_DVR_GetLastError()<<std::endl;
        }
    }
    /*
        * @Description:退出摄像头
    */    
    void HcCameraHandle::LogOut(){
        if(!NET_DVR_Logout(camera_param.lUserID)){
            std::cout<<"摄像头退出登录失败，错误值："<<NET_DVR_GetLastError()<<std::endl;
        }else{
            std::cout<<"摄像头退出登录成功！"<<camera_param.lUserID<<std::endl;
        }
    }
    /*
        * @Description:打开读取温度
    */
    void HcCameraHandle::ReadTemperature(){
        NET_DVR_REALTIME_THERMOMETRY_COND _thermometry ={0};
        _thermometry.dwSize = sizeof(_thermometry);// 结构体大小
        _thermometry.byRuleID = 1;// 规则ID
        _thermometry.dwChan = 1;// 通道号
        _thermometry.wInterval = 3;//读取间隔三秒，但感觉没什么区别，有空再测试
        camera_param.lTemperatureHandle = NET_DVR_StartRemoteConfig(camera_param.lUserID,
                                                                    NET_DVR_GET_REALTIME_THERMOMETRY,
                                                                    &_thermometry, 
                                                                    sizeof(_thermometry), 
                                                                    this->RemoteConfigCallback, //回调函数
                                                                    this);
        if(camera_param.lTemperatureHandle < 0){
            std::cout<<"温度读取失败，错误值："<<NET_DVR_GetLastError()<<std::endl;
        }else{
            std::cout<<"温度读取成功，返回值："<<camera_param.lTemperatureHandle<<std::endl;
        }
    }
    /*
        * @Description:关闭读取温度
    */
    void HcCameraHandle::CloseReadTemperature(){
        if(!NET_DVR_StopRemoteConfig(camera_param.lTemperatureHandle)){
            std::cout<<"关闭温度读取失败，错误值："<<NET_DVR_GetLastError()<<std::endl;
        }else{
            std::cout<<"关闭温度读取成功"<<camera_param.lTemperatureHandle<<std::endl;
        }
    }
    /*
        * @Description:打开声音获取
    */
    void HcCameraHandle::ReadVoice(){
        camera_param.lVoiceHanle = NET_DVR_StartVoiceCom_V30(camera_param.lUserID, 1,AUDIO_DATA_TYPE, this->fVoiceDataCallBack, this);
        if(camera_param.lVoiceHanle < 0){
            std::cout<<"声音读取失败，错误值："<<NET_DVR_GetLastError()<<std::endl;
        }else{
            std::cout<<"声音读取成功，返回值："<<camera_param.lVoiceHanle<<std::endl;
        }
    }
    /*
        * @Description:关闭声音获取
    */
    void HcCameraHandle::CloseReadVoice(){
        if(!NET_DVR_StopVoiceCom(camera_param.lVoiceHanle)){
            std::cout<<"关闭声音读取失败，错误值："<<NET_DVR_GetLastError()<<std::endl;
        }else{
            std::cout<<"关闭声音读取成功"<<camera_param.lVoiceHanle<<std::endl;
        }
    }
    /*
        * @Description:云台控制
    */
    void HcCameraHandle::PTZControl(void* args){
        std::string _url_param = *(std::string*)args;

        std::map<std::string, std::string> _params = SplitUrlParam(_url_param);
        DWORD _dwPTZCommand = atoi(_params["dwPTZCommand"].c_str());
        DWORD _dwSpeed = atoi(_params["dwSpeed"].c_str());
        DWORD _dwStop = atoi(_params["dwStop"].c_str());

        NET_DVR_PTZControlWithSpeed_Other(camera_param.lUserID,1,_dwPTZCommand,_dwStop,_dwSpeed);
    }
    /*
        * @Description:开始视频传输
    */
    void HcCameraHandle::VideoBegin(){
        camera_param.lRealPlayHandle = NET_DVR_RealPlay_V40(camera_param.lUserID, 
                                                    &camera_param.struPlayInfo, 
                                                    this->fRealDataCallBack,
                                                    this);//开始取流解码
        if(camera_param.lRealPlayHandle < 0){
            std::cout<<"预览播放失败，错误值："<<NET_DVR_GetLastError()<<std::endl;
        }else{
            std::cout<<"预览播放成功，返回值："<<camera_param.lRealPlayHandle<<std::endl;
        }
    }
    /*
        * @Description:停止视频传输
    */
    void HcCameraHandle::VideoStop(){
        if(!NET_DVR_StopRealPlay(camera_param.lRealPlayHandle)){
            std::cout<<"关闭温度读取失败，错误值："<<NET_DVR_GetLastError()<<std::endl;
        }else{
            std::cout<<"关闭温度读取成功"<<camera_param.lTemperatureHandle<<std::endl;
        }
    }
    /*
        * @Description:温度数据回调函数
    */
    void CALLBACK HcCameraHandle::RemoteConfigCallback(DWORD dwType, void *lpBuffer, DWORD dwBufLen, void *pUserData){ 
        HcCameraHandle *ptr = (HcCameraHandle *)pUserData;
        if (dwType == NET_SDK_CALLBACK_TYPE_DATA){
            LPNET_DVR_THERMOMETRY_UPLOAD _temperature_ptr = (LPNET_DVR_THERMOMETRY_UPLOAD)lpBuffer;
            //框/线测温
            if((_temperature_ptr->byRuleCalibType==1)||(_temperature_ptr->byRuleCalibType==2)){
                std::cout<<"max temp:"<<_temperature_ptr->struLinePolygonThermCfg.fMaxTemperature<<std::endl;
                std::cout<<"min temp:"<<_temperature_ptr->struLinePolygonThermCfg.fMinTemperature<<std::endl;
                std::cout<<"average temp:"<<_temperature_ptr->struLinePolygonThermCfg.fAverageTemperature<<std::endl;
            }
        }
    }
    /*
        * @Description:音视频流回调函数
    */
    void CALLBACK HcCameraHandle::fRealDataCallBack(LONG lRealHandle, DWORD dwDataType, BYTE *pBuffer, DWORD dwBufSize, void *pUser){
        HcCameraHandle *_ptr = (HcCameraHandle *)pUser;
        switch (dwDataType)
        {
            case NET_DVR_SYSHEAD: //系统头
                if (!PlayM4_GetPort(&_ptr->camera_param.nPort)){  //获取播放库未使用的通道号
                    std::cout<<"获取播放库号失败"<<std::endl;
                }
                if (!PlayM4_SetStreamOpenMode(_ptr->camera_param.nPort, STREAME_REALTIME)){  //设置实时流播放模式
                    std::cout<<"设置实时流播放模式失败"<<std::endl;
                }
                if (!PlayM4_OpenStream(_ptr->camera_param.nPort, pBuffer, dwBufSize, 10 * 1024 * 1024)){ //打开流接口
                    std::cout<<"打开流接口失败"<<std::endl;
                }
                if (!PlayM4_SetDecCallBack(_ptr->camera_param.nPort, NULL)){ //设置解码回调函数，获取解码后的数据,最后一个参数换成要回调的函数
                    std::cout<<"设置解码回调函数失败"<<std::endl;
                }
                if (!PlayM4_Play(_ptr->camera_param.nPort, NULL)){ //播放开始，最后一个参数设置播放窗口的话可以直接显示出来
                    std::cout<<"播放失败"<<std::endl;
                }
                if (!PlayM4_PlaySound(_ptr->camera_param.nPort)){ //打开音频解码, 需要码流是复合流
                    std::cout<<"音频播放失败"<<std::endl;
                } 
                break;
            case NET_DVR_STREAMDATA:
                //码流数据
                if (dwBufSize > 0 && _ptr->camera_param.nPort != -1){
                    if (!PlayM4_InputData(_ptr->camera_param.nPort, pBuffer, dwBufSize)){
                        std::cout << "error" << PlayM4_GetLastError(_ptr->camera_param.nPort) <<std::endl;
                        break;
                    }
                }
                break;
            default:
                break;
        }
    }
    /*
        * @Description:音频回调函数
    */
    void CALLBACK HcCameraHandle::fVoiceDataCallBack(LONG lVoiceComHandle, char *pRecvDataBuffer, DWORD dwBufSize, BYTE byAudioFlag, void*pUser){
        HcCameraHandle *_ptr = (HcCameraHandle *)pUser;
        std::cout<<"音频回调函数"<<std::endl;              
    }
    /*
        * @Description:异常回调函数
    */
    void CALLBACK HcCameraHandle::g_ExceptionCallBack(DWORD dwType, LONG lUserID, LONG lHandle, void *pUser){
        char tempbuf[256] = { 0 };
        switch (dwType)
        {
        case EXCEPTION_RECONNECT:    //预览时重连
            printf("----------reconnect--------%d\n", time(NULL));
            break;
        default:
            break;
        }
    }
    
}