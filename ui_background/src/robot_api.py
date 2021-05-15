robot_ip = "101.37.16.240"
robot_port = 62222
# robot_ip = "10.7.5.88"
# robot_port = 8080

API = {
    #real_time_data
    "odom_raw": "/gs-robot/real_time_data/odom_raw",    # 获取里程计数据
    "gps_raw" :"/gs-robot/real_time_data/gps_raw",  # 获取gps数据，这里应该是没处理的数据
    "cmd_vel" :"/gs-robot/real_time_data/cmd_vel" ,     # 获取实时角速度和线速度数据
    "scan_map_png" :"/gs-robot/real_time_data/scan_map_png", # 获取实时扫描地图 
    
    "position" :"/gs-robot/real_time_data/position",    # 初始化之后，可以获取机器人的实时位置
    "gps" :"/gs-robot/real_time_data/gps",  # 初始化之后，可以获取机器人的gps位置
    "navigate_path" :"/gs-robot/real_time_data/navigate_path", # 导航实时路线

    #data
    "device_status" :"/gs-robot/data/device_status",    # 获取设备状态数据
    "positions" :"/gs-robot/data/positions",#?map_name=?&type=?",  # 获取地图标记点的数据，type为空返回所有点，否则返回type表示类型的点
    "map_png" :"/gs-robot/data/map_png",#?map_name=?",   # 获取地图图片
    "maps" : "/gs-robot/data/maps", #获取地图列表

    #cmd
    "add_position" :"/gs-robot/cmd/add_position",#?position_name=?&type=?",  # 添加标记点
    "delete_positions" :"/gs-robot/cmd/delete_position",#?map_name=?&position_name=?", # 删除标记点
    "start_scan_map" :"/gs-robot/cmd/start_scan_map",    #map_name=?&type=?# 开始扫描地图，type=0新建，=1扩展地图
    "cancel_scan_map" :"/gs-robot/cmd/cancel_scan_map",  # 取消扫描，不保存地图
    "async_stop_scan_map" :"/gs-robot/cmd/async_stop_scan_map",   # 结束扫描，保存地图，异步
    "is_stop_scan_finished" :"/gs-robot/cmd/is_stop_scan_finished",  # 异步结束扫地图是否完成
    "delete_map" :"/gs-robot/cmd/delete_map", #?map_name=?",  # 删除地图
    "load_map" :"/gs-robot/cmd/load_map", #?map_name=?",  # 加载地图
    "initialize_directly" :"/gs-robot/cmd/initialize_directly",#?map_name=?&init_point_name=?",   # 不转圈初始化，
    "initialize" :"/gs-robot/cmd/initialize",#?map_name=?&init_point_name=?",   # 转圈初始化，要给定位置点，但不用方向
    "initialize_global" :"/gs-robot/cmd/initialize_global",#?map_name=?",  # 应该是自动行走确定在地图上的坐标点
    "is_initialize_finished" :"/gs-robot/cmd/is_initialize_finished",# 转圈初始化 是否完成
    "anywhere_navigate" : "/gs-robot/cmd/navigate", #post,从地图获取导航点，然后传给机器人
    "navigate" :"/gs-robot/cmd/position/navigate",#?map_name=?&position_name=?",  # 导航到指定地图的指定标记点
    "pause_navigate" :"/gs-robot/cmd/pause_navigate",   # 暂停导航
    "resume_navigate" :"/gs-robot/cmd/resume_navigate",   # 恢复导航
    "cancel_navigate" :"/gs-robot/cmd/cancel_navigate",   # 取消导航
    "move" :"/gs-robot/cmd/move", #post请求，传入线速度和角速度，都是-0.6 - 0.6，角速度负值右转，正值左转。
    "move_to" :"/gs-robot/cmd/move_to",#?distance=?&speed=?",   # 定速定距离移动，速度-0.6 - 0.6米/秒
    "is_move_to_finished" :"/gs-robot/cmd/is_move_to_finished",  # 判读定速定距离移动是否完成
    "stop_move_to" :"/gs-robot/cmd/stop_move_to",   # 停止定速定距离移动
    "clear_mcu_error" :"/gs-robot/cmd/clear_mcu_error",#?error_id=-1",  # 清除驱动器错误，不知道错误id默认传-1
    "power_off" :"/gs-robot/cmd/power_off",  # 关机，充电状态下才能关机
    "set_speed_level" :"/gs-robot/cmd/set_speed_level",#?level=?",  # 设置导航时移动速度，低中高，0 1 2,
    "stop_task_queue": "/gs-robot/cmd/stop_task_queue", #停止所有队列任务
    "start_task_queue": "/gs-robot/cmd/start_task_queue",#开始队列任务
    "resume_task_queue": "/gs-robot/cmd/resume_task_queue", #恢复队列任务
    "cancle_task_queue": "/gs-robot/cmd/cancle_task_queue", #恢复队列任务
    "on_map_add_position": "/gs-robot/cmd/position/add_position", #post 
    "ptz_control" : "/gs-robot/cmd/ptz_control",#dwPTZCommand=?&dwSpeed=?&dwStop=?
    "open_video" : "/gs-robot/cmd/open_video", #向服务器查询视频是否打开
    "close_video" : "/gs-robot/cmd/close_video", #关闭视频传输
    "power_off" : "/gs-robot/cmd/power_off", #交互模块关机
    "open_light": "/gs-robot/cmd/open_light", #打开报警灯
    "open_trumpet": "/gs-robot/cmd/open_trumpet",#打开喇叭
    "close_light": "/gs-robot/cmd/close_light", #关闭报警灯
    "close_trumpet": "/gs-robot/cmd/close_trumpet",#关闭喇叭
}

PTZ_Command = {
    "ZOOM_IN" : 11, #倍率变大
    "ZOOM_OUT" : 12, #倍率变小
    "TILT_UP" : 21, #云台上仰
    "TILT_DOWN" : 22, #云台下俯
    "PAN_LEFT" : 23, #云台左转
    "PAN_RIGHT" : 24, #云台右转
    "UP_LEFT" : 25, #云台上仰和左转
    "UP_RIGHT" : 26, #云台上仰和右转
    "DOWN_LEFT" : 27, #云台下俯和左转
    "DOWN_RIGHT" : 28, #云台下俯和右转
    "PAN_AUTO" : 29, # 云台左右自动扫描
}


