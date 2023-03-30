import ctypes
import struct
from ctypes import Structure, c_int, c_char_p, create_string_buffer, memmove, c_void_p, c_size_t

class BcosReqContext(Structure):
    _fields_ = [('seq', c_int),
                ('name', c_char_p),
                ('msg', c_char_p),
                ]
    
    def __init__(self, s, n, m):
        self.seq = s
        self.name = n.encode("utf-8")
        self.msg = m.encode("utf-8")
    
    def detail(self):
        s = f"seq:{self.seq},name:{self.name},msg:{self.msg}";
        return s


'''
//c语言定义的返回结构体
struct bcos_sdk_c_struct_response
{
    int error;   // 返回状态, 0成功, 其他失败
    char* desc;  // 失败时描述错误信息
    void* data;   // 返回数据, error=0 时有效
    size_t size;  // 返回数据大小, error=0 时有效
    void* context;  // 回调上下文,调用接口时传入的`context`参数
};
'''


class BcosResponse:
    error = 0
    desc =  ""
    data=  ""
    size = 0
    context: BcosReqContext = None

    def __init__(self, c_resp):
        self.extract_response(c_resp)
     
    def extract_response(self, c_resp):
        if c_resp == None:
            return
        self.size = c_resp.contents.get_size()
        pool = create_string_buffer(c_resp.contents.size)
        memmove(pool, c_resp.contents.data, c_resp.contents.size)
        self.data = b2s(pool.value)
        self.error = c_resp.contents.get_error()
        if self.error != 0:
            self.desc = b2s(c_resp.contents.desc)
        else:
            self.desc = ""
        self.context_callback = c_resp.contents.get_context()
        return self
    
    def detail(self):
        str = f"error:{self.error},size:{self.size},data:{self.data},desc:{self.desc}."
        c = self.context_callback
        if c is not None:
            str = str + (" | context:({}),{},[{}]".format(c.seq, b2s(c.name), b2s(c.msg)))
        return str


# bcos sdk返回结构体,ctype定义
class BcosResponseCType(Structure):
    _fields_ = [('error', c_int),
                ('desc', c_char_p),
                ('data', c_void_p),
                ('size', c_size_t),
                ('context', c_void_p),
                ]
    
    def get_data_str(self):
        pool = create_string_buffer(self.size)
        memmove(pool, self.data, self.size)
        return b2s(pool)
    
    def get_desc(self):
        if self.desc is None:
            return ""
        return b2s(self.desc)
    
    def get_size(self):
        return self.size
    
    def get_error(self):
        return self.error
    
    def get_context(self):
        c = ctypes.cast(self.context, ctypes.POINTER(BcosReqContext))
        return c.contents


# cyber2023.3 by kent
def strarr2ctypes(data):
    C_TOPIC_ARRAY = c_char_p * len(data)
    ctypetopic = C_TOPIC_ARRAY()
    for i in range(0, len(data)):
        ctypetopic[i] = (c_char_p)(s2b(data[i]))
    return ctypetopic


# cyber2023.3 by kent
def s2b(data):
    """
    将Python数据类型转换为bytes类型
    :param data: 需要转换的数据
    :return: 转换后的bytes类型数据
    """
    """
    将Python数据类型转换为bytes类型
    :param data: 需要转换的数据
    :return: 转换后的bytes类型数据
    """
    if isinstance(data, str):
        return data.encode('utf-8')
    elif isinstance(data, int):
        return data.to_bytes(4, byteorder='big')
    elif isinstance(data, float):
        return struct.pack('f', data)
    elif isinstance(data, bool):
        return int(data).to_bytes(1, byteorder='big')
    elif data is None:
        return b''
    elif isinstance(data, bytes):
        return data
    else:
        raise TypeError(f"不支持的数据类型转换为bytes类型，方法名：{s2b.__name__}，输入参数类型：{type(data)}")


def b2s(input):
    if type(input) is bytes:
        try:
            return str(input, "UTF-8")
        except Exception as e:
            return input
    return input



# bcos sdk回调函数定义
# typedef void (*bcos_sdk_c_struct_response_cb)(struct bcos_sdk_c_struct_response* resp)
BCOS_CALLBACK_FUNC = ctypes.CFUNCTYPE(None, ctypes.POINTER(BcosResponseCType))

# typedef void (*bcos_sdk_c_amop_subscribe_cb)(
# const char* endpoint, const char* seq, struct bcos_sdk_c_struct_response* resp);
BCOS_AMOP_SUB_CALLBACK_FUNC = ctypes.CFUNCTYPE(None, c_char_p, c_char_p, ctypes.POINTER(BcosResponseCType))
BCOS_AMOP_PUBLISH_CALLBACK_FUNC = ctypes.CFUNCTYPE(None, ctypes.POINTER(BcosResponseCType))


