#include <stdio.h>
#include <stdlib.h>
#include <linux/i2c-dev.h>
#include <fcntl.h>
#include <termios.h>

enum {
I2C_ERR_SUCCSESS,		//	0-succses
I2C_ERR_OPENING_DEVICE,		//	1-error opening i2c bus
I2C_ERR_ASSIGN_ADDR,		//	2-error assigning i2c addres
I2C_ERR_READ_DATA,		//	3-error write data to i2c bus
I2C_ERR_WRITE_DATA,		//	4-error read data from i2c bus
};


int fd=0;

int open_dev(const char *name, int baudrate)
{
	fd=open(name,O_RDWR);
	if(fd==-1){
		printf("Can't open file %s\n",name);
		return -1;	
	}
	printf("int open_i2cbus(%s,%i)\n",name,baudrate);

	struct termios options;
	tcgetattr(fd,&options);
	cfsetispeed(&options,baudrate);
	cfsetospeed(&options,baudrate);
	int res;
	res=cfgetospeed(&options);
	printf("Baudrate: %i\n",res);
	options.c_cflag|=CS8;
	options.c_cflag&=~PARENB;
	tcsetattr(fd, TCSANOW, &options);

	return 1;
}

//===========================================================================================

int write_to_dev(void *data,int size)
{
	unsigned char *cdata=(unsigned char *)data;
	int i;
//	printf ("size = %i\n",size);
//	for(i=0;i<size;i++)
//		printf("data[%i] : %i\n",i,cdata[i]);
	
	int count_wr_byte=write(fd,cdata,size);
	printf ("int write_to_i2cbus()::count write byte : %i\n",count_wr_byte);
	if(count_wr_byte!=size){
		printf("int write_to_i2cbus()::Error write data to i2c device.\n");
		return -1;		
	}
	
	printf("int write_to_i2cbus()::ok\n");
	return count_wr_byte;
}

//===========================================================================================

int read_from_dev(void *data, int size)
{
	unsigned char *cdata=(unsigned char *)data;
	int count_rd_byte=read(fd,cdata,size);
	printf ("int read_from_i2cbus()::count read byte : %i\n",count_rd_byte);
	if(count_rd_byte!=size){
		printf("int read_from_i2cbus()::Error read data from i2c divice.\n")	;
		return -1;
	}	
	return count_rd_byte;
}



int close_dev()
{
	if(close(fd)==-1){
		printf("Can't close fd.\n");
		return -1;
	}
	printf("int close_i2cbus()::ok\n");
	return 1;
}














