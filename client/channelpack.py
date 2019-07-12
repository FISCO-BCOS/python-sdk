import uuid
import struct
from client import  clientlogger
'''


0x12	以太坊消息	SDK->节点
0x13	心跳包	SDK->节点
0x30	AMOP请求包	SDK->节点
0x31	AMOP响应包	SDK->节点
0x32	上报Topic信息	SDK->节点
0x10000	交易上链回调	节点->SDK

lenght	uint32_t	数据包长度，含包头和数据，最大长度为10M Byte
type	uint16_t	数据包类型
seq	string	数据包序列号，32字节，SDK传入
result	int	处理结果
data	vector	数据本身

'''
from eth_utils import *
type = 0x12
data = "1234567890"
'''
lenght	uint32_t	数据包长度，含包头和数据，最大长度为10M Byte
type	uint16_t	数据包类型
seq	string	数据包序列号，32字节，SDK传入
result	int	处理结果
data	vector	数据本身
'''


class ChannlePack:
    TYPE_RPC=0x12
    headerfmt = "!IH32sI"
    type = None
    result = None
    data = None

    @staticmethod
    def pack(type,data):
        headerlen = struct.calcsize(ChannlePack.headerfmt)
        databytes = bytes(data, "utf-8")
        datalen = len(databytes)
        seq = uuid.uuid1()
        seq32 = "".join(str(seq).split("-")).upper()
        seq32byte =bytes(seq32, encoding='utf-8')

        fmt = "!IH32sI%ds" % (len(data))
        totallen = headerlen + len(data)
        result = 0
        buffer = struct.pack(fmt, totallen, type, seq32byte, result, databytes)
        return buffer

    @staticmethod
    #return（code, 消耗的字节数，解析好的cp或None）
    def unpack(buffer):
        totallen = struct.unpack_from("!I",buffer,0)[0]
        clientlogger.logger.debug("total bytes to decode {}, datalen {}".format(totallen,len(buffer)))
        if(len(buffer) <totallen ):
            #no enough bytes to decode
            return (-1,0,None)
        headerlen = struct.calcsize(ChannlePack.headerfmt)
        datalen =  len(buffer) - headerlen
        (totallen,type,seq,result) = struct.unpack_from(ChannlePack.headerfmt, buffer,0)
        data = struct.unpack_from("%ds"%datalen,buffer,headerlen)[0]
        cp = ChannlePack()
        cp.result = result
        cp.data = data.decode("utf-8")
        cp.type = type
        return (0,totallen,cp)



'''
x	pad byte	no value	 	 
c	char	string of length 1	1	 
b	signed char	integer	1	(3)
B	unsigned char	integer	1	(3)
?	_Bool	bool	1	(1)
h	short	integer	2	(3)
H	unsigned short	integer	2	(3)
i	int	integer	4	(3)
I	unsigned int	integer	4	(3)
l	long	integer	4	(3)
L	unsigned long	integer	4	(3)
q	long long	integer	8	(2), (3)
Q	unsigned long long	integer	8	(2), (3)
f	float	float	4	(4)
d	double	float	8	(4)
s	char[]	string	1	 
p	char[]	string	 	 
P	void *	integer	 	(5), (3)
'''