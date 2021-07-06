cmake_minimum_required(VERSION 2.8)
project(demo)
add_compile_options(-std=c++11)


find_package( OpenCV REQUIRED )
include_directories(${OpenCV_INCLUDE_DIRS})

include_directories( ${CMAKE_CURRENT_SOURCE_DIR}/include)
#ADD_SUBDIRECTORY
# add_executable(test_cmd ./src/cmd.cpp)
# SET(LIBRARY_OUTPUT_PATH ${CMAKE_CURRENT_SOURCE_DIR}/lib)#设置库文件生成的路径

# add_library(video_handle SHARED ./src/lib_video_handle.cpp)#生成库文件

link_directories(${CMAKE_CURRENT_SOURCE_DIR}/libs)#要链接的库的路径

add_executable(video_trans ./src/trans_video_all.cpp ./src/lib_video_handle.cpp)
target_link_libraries(video_trans libhcnetsdk.so)
target_link_libraries(video_trans libHCCore.so)
target_link_libraries(video_trans libhpr.so)
target_link_libraries(video_trans libStreamTransClient.so)
target_link_libraries(video_trans ${OpenCV_LIBS})
target_link_libraries(video_trans libPlayCtrl.so libSuperRender.so)
target_link_libraries(video_trans pthread.so)
target_link_libraries(video_trans libmsc.so)
target_link_libraries(video_trans libw_ivw.so)

add_executable(video_decode ./src/decode_video_all.cpp ./src/lib_video_handle.cpp)
target_link_libraries(video_decode libhcnetsdk.so)
target_link_libraries(video_decode libHCCore.so)
target_link_libraries(video_decode libhpr.so)
target_link_libraries(video_decode libStreamTransClient.so)
target_link_libraries(video_decode ${OpenCV_LIBS})
target_link_libraries(video_decode libPlayCtrl.so libSuperRender.so)
target_link_libraries(video_decode pthread.so)
target_link_libraries(video_decode libmsc.so)
target_link_libraries(video_decode libw_ivw.so)

# add_executable(red_video_trans ./src/main_local.cpp)
# target_link_libraries(red_video_trans libhcnetsdk.so)
# target_link_libraries(red_video_trans libHCCore.so)
# target_link_libraries(red_video_trans libhpr.so)
# target_link_libraries(red_video_trans libStreamTransClient.so)
# target_link_libraries(red_video_trans ${OpenCV_LIBS})
# target_link_libraries(red_video_trans libPlayCtrl.so libSuperRender.so)
# target_link_libraries(red_video_trans pthread.so)

# add_executable(red_video_decode ./src/decode_video_red.cpp)
# target_link_libraries(red_video_decode libhcnetsdk.so)
# target_link_libraries(red_video_decode libHCCore.so)
# target_link_libraries(red_video_decode libhpr.so)
# target_link_libraries(red_video_decode libStreamTransClient.so)
# target_link_libraries(red_video_decode ${OpenCV_LIBS})
# target_link_libraries(red_video_decode libPlayCtrl.so libSuperRender.so)
# target_link_libraries(red_video_decode pthread.so)


# SET(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE) 
# SET(CMAKE_INSTALL_RPATH ${CMAKE_CURRENT_SOURCE_DIR}/libs) #指定运行时动态库的加载路径,ORIGIN指运行文件所在目录
# SET(CMAKE_INSTALL_RPATH "\${ORIGIN}/lib") #指定运行时动态库的加载路径,ORIGIN指运行文件所在目录
# ${ORIGIN}是指运行程序所在目录，如果你的lib放在其它路径下，你就改为你的路径即可