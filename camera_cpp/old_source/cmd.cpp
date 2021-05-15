#include <iostream>
#include <string.h>
#include "VideoHandle.h"
#include <map>
#include <vector>

using namespace std;
// string robot_ip = "10.7.5.88";
// long int robot_port = 8080;

// //real_time_data
// #define odom_raw "/gs-robot/real_time_data/odom_raw" //获取里程计数据
// #define gps_raw "/gs-robot/real_time_data/gps_raw" //获取gps数据，这里应该是没处理的数据
// #define cmd_vel "/gs-robot/real_time_data/cmd_vel" //获取实时角速度和线速度数据
// #define scan_map_png "/gs-robot/real_time_data/scan_map_png" //获取实时扫描地图
// #define position "/gs-robot/real_time_data/position" //初始化之后，可以获取机器人的实时位置
// #define gps "/gs-robot/real_time_data/gps" //初始化之后，可以获取机器人的gps位置
// #define navigate_path "/gs-robot/real_time_data/navigate_path" //导航实时路线

// //data
// #define device_status "/gs-robot/data/device_status" //获取设备状态数据
// #define positions "/gs-robot/data/positions?map_name=?&type=?"//获取地图标记点的数据，type为空返回所有点，否则返回type表示类型的点
// #define map_png "/gs-robot/data/map_png?map_name_name=?"//获取地图图片

// //cmd
// #define add_positions "/gs-robot/cmd/add_positions?position_name=?&type=?"//添加标记点
// #define delete_positions "/gs-robot/cmd/delete_positions?map_name=?&type=?"//删除标记点
// #define start_scan_map "/gs-robot/cmd/start_scan_map?map_name=?&type=?"//开始扫描地图，type=0新建，=1扩展地图
// #define cancel_scan_map "/gs-robot/cmd/cancel_scan_map" //取消扫描，不保存地图
// #define async_stop_scan_map "/gs-robot/cmd/async_stop_scan_map" //结束扫描，保存地图，异步
// #define is_stop_scan_map "/gs-robot/cmd/is_stop_scan_map" //异步结束扫地图是否完成
// #define delete_map "/gs-robot/cmd/delete_map?map_name=?"//删除地图
// #define load_map "/gs-robot/cmd/load_map?map_name=?"//加载地图
// #define initialize "/gs-robot/cmd/initialize?map_name=?&init_point_name=?"//转圈初始化，要给定位置点，但不用方向
// #define initialize_global "/gs-robot/cmd/initialize_global?map_name=?" //应该是自动行走确定在地图上的坐标点
// #define navigate "/gs-robot/cmd/position/navigate?map_name=?&position_name=?"//导航到指定地图的指定标记点
// #define pause_navigate "/gs-robot/cmd/pause_navigate" //暂停导航
// #define resume_navigate "/gs-robot/cmd/resume_navigate" //恢复导航
// #define cancel_navigate "/gs-robot/cmd/cancel_navigate" //取消导航
// #define move_to "/gs-robot/cmd/move_to?distance=?&speed=?"//定速定距离移动，速度-0.6--0.6米/秒
// #define is_move_to_finished "/gs-robot/cmd/is_move_to_finished" //判读定速定距离移动是否完成
// #define stop_move_to "/gs-robot/cmd/stop_move_to" //停止定速定距离移动
// #define clear_mcu_error "/gs-robot/cmd/clear_mcu_error?error_id=-1" //清除驱动器错误，不知道错误id默认传-1
// #define power_off "/gs-robot/cmd/power_off" //关机，充电状态下才能关机
// #define set_speed_level "/gs-robot/cmd/set_speed_level?level=?" //设置导航时移动速度，低中高，0 1 2

void fun1(void *args)
{   
    string* t = (string*)args;
    cout<<t<<endl;
    cout<<*t<<endl;
}

void fun(void *args)
{   
    LONG* t = (LONG*)args;
    fun1(t);
    cout<<"竟然可以"<<endl;
}
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

int main(){
    int i=100;
    string url = "ghf=3&ghs=4&ngmg=5";
    std::map<std::string, std::string> res = split_url_param(url);
    std::map<std::string, std::string>::iterator   iter;
    for(iter = res.begin(); iter != res.end(); iter++){
        cout<<iter->first<<" "<<iter->second<<endl;
    }
    // while(i++){
    //     if(i%2){
    //         url = "ning?ghf=3&ghs=4";
    // // fun1(&url);
    // // cout<<&url<<endl;
    //     }
    //     else{
    //         url = "ning";
    //     }
    //     cout<<url<<endl;
    //     string::size_type pos = url.find("?");
    //     if(pos!=string::npos){//还有参数
    //         std::vector<std::string> result=split(url,"?");
    //         string url_cmd = result[0];
    //         string url_param = result[1];
    //         cout<<url_cmd<<endl;
    //         cout<<&url_cmd<<endl;
    //     }
    //     else{
    //         string url_cmd = url;
    //         cout<<url_cmd<<endl;
    //         cout<<&url_cmd<<endl;
    //     }
    //     cout<<endl;
    //     if(i>110)
    //         break;
    //     }

    // CameraParam normal_camera;
    // std::map<std::string, create_fun> mymap;
    // mymap["fun"] = fun;
    // std::map<std::string, create_fun>::iterator it = mymap.find("fun");
    // create_fun func = it->second;

    // cout<<normal_camera.struPlayInfo.lChannel<<endl;
}