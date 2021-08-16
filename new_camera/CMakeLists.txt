cmake_minimum_required(VERSION 2.8)
project(camera_sample)
add_compile_options(-std=c++11)


find_package( OpenCV REQUIRED )
include_directories(${OpenCV_INCLUDE_DIRS})
include_directories(${PROJECT_SOURCE_DIR}/include)

link_directories(${PROJECT_SOURCE_DIR}/libs)#要链接的库的路径

file(GLOB_RECURSE ALL_TARGET_LIBRARIES "*.so")
list(APPEND ALL_TARGET_LIBRARIES ${OpenCV_LIBS})

file(GLOB_RECURSE ALL_SRCS "*.cpp")

file(GLOB_RECURSE NODE_SRCS "src/*_node.cpp")
file(GLOB_RECURSE REMOVE_CMAKE "build/*.cpp")
list(REMOVE_ITEM ALL_SRCS ${NODE_SRCS})
list(REMOVE_ITEM ALL_SRCS ${REMOVE_CMAKE})

add_executable(camera_message_node src/camera_message_node.cpp ${ALL_SRCS})
target_link_libraries(camera_message_node ${ALL_TARGET_LIBRARIES})


# SET(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE) 
# SET(CMAKE_INSTALL_RPATH ${CMAKE_CURRENT_SOURCE_DIR}/libs) #指定运行时动态库的加载路径,ORIGIN指运行文件所在目录
# SET(CMAKE_INSTALL_RPATH "\${ORIGIN}/lib") #指定运行时动态库的加载路径,ORIGIN指运行文件所在目录
# ${ORIGIN}是指运行程序所在目录，如果你的lib放在其它路径下，你就改为你的路径即可