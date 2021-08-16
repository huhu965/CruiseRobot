/* 
 * @Author: Hu Ziwei
 * @Description: 存放一些自定义的功能函数和用到大部分库的头文件
 * @Date: 2021-07-15 19:58:48
 * @Last Modified by: Hu Ziwei
 * @Last Modified time: 2021-07-19 15:04:06
 * @命名规则
 *   1.类名和方法命名用驼峰，FunName
 *   2.类内变量，全部小写，下划线分割，param_name
 *   3.类内私有的变量和方法统一在最后加下划线，FunNam_;param_name_
 *   4.函数内临时变量统一在前面加下划线，_param_name
 *   5.方法名带数字驼峰不好阅读时，加_下划线分割，Transform_Tyv12_To_Cv8uc3
 */
#ifndef ROBOT_BACKGROUND_BASE_FUNC_HPP_
#define ROBOT_BACKGROUND_BASE_FUNC_HPP_

#include <iostream>
#include "string"
#include <vector>
#include <map>
#include <unistd.h>

#include "hc/HCNetSDK.h"
#include "hc/LinuxPlayM4.h"

#include <opencv2/opencv.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui_c.h>

//////////////////格式转换和字符串操作功能函数//////////////////////////////
/*
    * @Function Description:把tuv12转为cv8uc3格式
    * @Params:
    * @Returns:
*/                                   
std::string  Transform_Tyv12_To_Cv8uc3(char * pBuf, int nSize, FRAME_INFO * pFrameInfo);

/*
    * @Function Description:音频8k转16k，同一个字符复制一次插入
    * @Params:
        pInAudioData 输入8k数据
        nInAudioLen 数据长度
        pOutAudioData 输出16k数据
        nOutAudioLen 输出数据大小
    * @Returns:
*/
void Extened_8k_To_16k(short* pInAudioData, int nInAudioLen, short* pOutAudioData, int& nOutAudioLen);

/*
    * @Function Description:字符串分割函数，将str按照pattern里的字符串分割开
    * @Params:
    *  str 输入的字符串
    *  pattern 按pattern对str进行分割
    * @Returns:
*/
std::vector<std::string> Split(std::string str, std::string pattern);

/*
    * @Function Description:get请求url携带param的分割函数，将参数名称和数据放入map中
    * @Params:
    * @Returns:
*/
std::map<std::string, std::string> SplitUrlParam(std::string url_param);

#endif