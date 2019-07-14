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


lenght	uint32_t	数据包长度，含包头和数据，最大长度为10M Byte
type	uint16_t	数据包类型
seq	string	数据包序列号，32字节，SDK传入
result	int	处理结果
data	vector	数据本身
'''


class ChannelPack:
    TYPE_RPC=0x12
    TYPE_HEATBEAT = 0x13
    TYPE_AMOP_REQ=0x30
    TYPE_AMOP_RESP = 0x31
    TYPE_TOPIC_REPORT = 0x32
    TYPE_TX_COMMITED = 0x10000

    headerfmt = "!IH32sI"
    headerlen = 0
    type = None
    result = None
    data = None
    seq = None
    totallen = None


    def detail(self):
        msg ="len:{},type:{},result:{},seq:{},data:{}"\
            .format(self.totallen,hex(self.type),hex(self.result),self.seq,self.data)
        return msg


    @staticmethod
    def getheaderlen():
        if ChannelPack.headerfmt == 0:
            ChannelPack.headerfmt = struct.calcsize(ChannelPack.headerfmt)
        return ChannelPack.headerlen

    @staticmethod
    def pack(type,seq,data):
        headerlen = struct.calcsize(ChannelPack.headerfmt)
        databytes = data
        if not isinstance(databytes,bytes):
            databytes = bytes(data,"utf-8")
        datalen = len(databytes)
        fmt = "!IH32sI%ds" % (len(data))
        totallen = headerlen + len(data)
        result = 0
        buffer = struct.pack(fmt, totallen, type, seq, result, databytes)
        return buffer

    @staticmethod
    #return（code, 消耗的字节数，解析好的cp或None）
    def unpack(buffer):
        headerlen = struct.calcsize(ChannelPack.headerfmt)
        if(len(buffer) < headerlen):
            return (-1,0,None)
        totallen = struct.unpack_from("!I",buffer,0)[0]
        clientlogger.logger.debug("total bytes to decode {}, datalen {}".format(totallen,len(buffer)))
        if(len(buffer) <totallen ):
            #no enough bytes to decode
            return (-1,0,None)
        datalen =  len(buffer) - headerlen
        (totallen,type,seq,result) = struct.unpack_from(ChannelPack.headerfmt, buffer, 0)
        data = struct.unpack_from("%ds"%datalen,buffer,headerlen)[0]
        cp = ChannelPack()
        cp.result = result
        cp.data = data
        cp.type = type
        cp.seq = seq
        cp.totallen = totallen
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