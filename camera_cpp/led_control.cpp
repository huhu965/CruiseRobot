#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <sys/io.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <getopt.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <errno.h>
#include <limits.h>
#include <signal.h>
#include <syslog.h>
#include <sys/time.h>
#include <sys/ioctl.h>

#include "sio_gpio.h"

#define BYPASS_VERSION "$Revision: 1.00 $"

const char *usage = "Usage: %s [options] file\n";
char *progname;
int fd = -1;

static void exit_soft(int sig);
int set_all_port(unsigned char state);
int set_port(unsigned short port,unsigned char state);
int get_port(unsigned short port,unsigned char* state);
void init_preport();
void poll_all_port_status();

int main(int argc, char **argv)
{
	unsigned char is_all = 0, port_number,port = 0,value=1,poll_all = 0 ,set_flag = 0;
	char cport[255],cvalue[255];
	progname = argv[0];
	int ret,portv,loops;
	int opt;
	unsigned char bpvalue;
	struct sigaction action;

	port = 1;
	printf("getopt -p value %d\n", port);
	value = 1;
	set_flag = 1;
	printf("getopt -s value %d\n", value);
  
	action.sa_handler = exit_soft;
	sigemptyset(&action.sa_mask);
	action.sa_flags = SA_RESTART | SA_SIGINFO;
	sigaction(SIGTERM, &action, NULL );
	sigaction(SIGINT, &action, NULL );
/****************************************************************************************************************************
*** 以下为操作gpio功能
****************************************************************************************************************************/
	//打开库
	printf("start open lib!\n");
	fd = open("/dev/hzx_gpio",O_RDWR);
	if(fd == -1){
		printf("%s open lib fail!\n", progname);
		exit(EXIT_FAILURE);
	}
	
	if(is_all && set_flag){
			set_all_port(value);//将全部端口设定为指定的value值
	}
	else if(port && set_flag) {
			set_port((port-1),value);	
	}
	else if(poll_all){
		poll_all_port_status();
	}

  	close(fd);
/****************************************************************************************************************************
*** 以上为操作gpio功能
****************************************************************************************************************************/
	return 0;
}

int set_all_port(unsigned char state)
{
	set_port(GPIO_PIN_2,state);
	set_port(GPIO_PIN_4,state);
	set_port(GPIO_PIN_6,state);
	set_port(GPIO_PIN_8,state);
}

int set_port(unsigned short port ,unsigned char state)
{
	int retval;
	unsigned char port_index = (unsigned char)port;
	int setv = state;
	
	switch(port){
		case GPIO_PIN_2:
		case GPIO_PIN_4:
		case GPIO_PIN_6:
		case GPIO_PIN_8:
			if(setv){
				retval = ioctl(fd,SET_GPIO_HIGHLEVEL,&port_index);
				printf("set port %d value is %d\n",port+1,setv);
				if(retval < 0){
					printf("Set gpio %d high level failed, err:%s\n",port_index+1,strerror(errno));
	  			return -1;
				}
			}
			else{
				retval = ioctl(fd,SET_GPIO_LOWLEVEL,&port_index);
				printf("set port %d value is %d\n",port+1,setv);
				if(retval < 0){
					printf("Set gpio %d low level failed, err:%s\n",port_index+1,strerror(errno));
	  			return -1;
				}				
			}
			break;			
		case GPIO_PIN_1:
		case GPIO_PIN_3:
		case GPIO_PIN_5:
		case GPIO_PIN_7:
			printf("Port %d is a input port,can't write to value\n", port+1);
			break;
		default:
			break;	
	}
	return 0;
}

int get_port(unsigned short port ,unsigned char* state)
{
	int retval;
	int setv = port;
	
	retval = ioctl(fd,GET_GPIO_LEVEL,&setv);
	if(retval < 0){
		printf("Get gpio %d status ioctl failed err:%s\n",port,strerror(errno));
	  return -1;
	}
	*state = (unsigned char)setv;
	return 0;
}

static void exit_soft(int sig)
{
	int retval;
  
 	retval = close(fd);
	if (retval == -1){
		printf("exit function close file failed!next time you can not oprate device,you must be restart you system\n");
	}
	else
		printf("exit function close file successful!\n");

	fd = -1;
  exit(EXIT_SUCCESS);
}

void init_preport(unsigned char* status)
{
	unsigned char iloop = 0;
	unsigned char pvalue;
	if(-1 == fd)
		return;
		
	for(;iloop < 8;iloop++){
		if(0 == get_port(iloop,&pvalue)){
			*(status+iloop) = (unsigned char)pvalue;
		}
	}
}

void poll_all_port_status()
{
	unsigned char pre_port_status[]={1,0,1,0,1,0,1,0};
	unsigned char current_status,test_num = 0;
	if(fd == -1)
		return;
		
	init_preport(pre_port_status);
	
	while(1){
		if(0 == get_port(test_num ,&current_status)){
			if(current_status != pre_port_status[test_num]){
				printf("port %d status changed,from %d to %d\n",(test_num+1),pre_port_status[test_num],current_status);
				*(pre_port_status+test_num) = current_status;
			}
		}
		else{
			printf("get port %d status failed\n",(test_num+1));
		}
		test_num = (++test_num > 7 ? 0 : test_num );
		usleep(10*1000);
	}
}