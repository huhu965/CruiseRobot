/* 
 * @Author: Hu Ziwei
 * @Description: 
 * @Date: 2021-07-15 20:11:28
 * @Last Modified by: Hu Ziwei
 * @Last Modified time: 2021-07-15 20:11:28 
 * @命名规则
 *   1.类名和方法命名用驼峰，FunName
 *   2.类内变量，全部小写，下划线分割，param_name
 *   3.类内私有的变量和方法统一在最后加下划线，FunNam_;param_name_
 *   4.函数内临时变量统一在前面加下划线，_param_name
 *   5.方法名带数字驼峰不好阅读时，加_下划线分割，Transform_Tyv12_To_Cv8uc3
*/

#include "robot_background/base_func.hpp"

std::vector<std::string> Split(std::string str, std::string pattern)
{
    std::string::size_type pos;
    std::vector<std::string> result;
    try{
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
    }catch(...){
        std::cout<<"字符串分割错误：给定的参数存在错误"<<std::endl;
    }
    
    return result;
}

std::map<std::string, std::string> SplitUrlParam(std::string url_param)
{
    std::map<std::string, std::string> result;
    std::vector<std::string> params = Split(url_param, "&");
    for(int i=0,n_size = params.size();i<n_size;i++)
    {
        std::vector<std::string> param = Split(params[i], "=");
        result[param[0]] = param[1];
    }
    return result;
}

std::string Transform_Tyv12_To_Cv8uc3(char * pBuf, int nSize, FRAME_INFO * pFrameInfo)
{
    cv::Mat pImg(pFrameInfo->nHeight, pFrameInfo->nWidth, CV_8UC3);
    cv::Mat src(pFrameInfo->nHeight + pFrameInfo->nHeight / 2, pFrameInfo->nWidth, CV_8UC1, pBuf);
    cvtColor(src, pImg, CV_YUV2BGR_YV12);//转为bgr格式

    std::vector<uchar> im_buf;
    std::vector<int> param;
    param.push_back(cv::IMWRITE_JPEG_QUALITY);
    param.push_back(80);//解码后图片的压缩质量，数越大质量越高，数据量越大
    cv::imencode(".jpg", pImg, im_buf,param);
    std::string str_img(im_buf.begin(), im_buf.end());

    //去掉注释可以将图片显示出来
    // cv::imshow("IPCamera", pImg);
    // cv::waitKey(1);

    return str_img;
}

void Extened_8k_To_16k(short* pInAudioData, int nInAudioLen, short* pOutAudioData, int& nOutAudioLen)
{   //short占两个字节
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
