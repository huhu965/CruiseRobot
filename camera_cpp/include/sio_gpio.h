#ifndef _T_OEM_CTRL_H
#define _T_OEM_CTRL_H

#include <linux/ioctl.h>
#include <linux/types.h>

#define BIT0                        0x01
#define BIT1                        0x02
#define BIT2                        0x04
#define BIT3                        0x08
#define BIT4                        0x10
#define BIT5                        0x20
#define BIT6                        0x40
#define BIT7                        0x80

#define GPIO_PIN_1                  0x00
#define GPIO_PIN_2                  0x01
#define GPIO_PIN_3                  0x02
#define GPIO_PIN_4                  0x03
#define GPIO_PIN_5                  0x04
#define GPIO_PIN_6                  0x05
#define GPIO_PIN_7                  0x06
#define GPIO_PIN_8                  0x07

#define TAIO_MAX_NR                     2

#define	TAIO_IOCTL_BASE	'H'

#define SET_GPIO_LOWLEVEL               _IOWR(TAIO_IOCTL_BASE,0,int)
#define SET_GPIO_HIGHLEVEL              _IOWR(TAIO_IOCTL_BASE,1,int)
#define GET_GPIO_LEVEL                  _IOR(TAIO_IOCTL_BASE,2,int)

#endif  //_XBROTHER_T_OEM_CTRL_H