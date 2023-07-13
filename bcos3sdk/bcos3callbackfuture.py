import queue

from bcos3sdk.bcos3datadef import BcosReqContext, BCOS_CALLBACK_FUNC, BCOS_AMOP_SUB_CALLBACK_FUNC, \
    BCOS_AMOP_PUBLISH_CALLBACK_FUNC, BcosResponse

G_SEQ = 0


# 模拟一个Future对象，用于接收回调，提供一个wait方法，把异步变成同步
# 采用queue来模拟wait，原因是一个future里有可能多次被回调,回调的消息put到queue里，应用端可以用wait方法依次将消息pop出来
# 注意，在此版本里，建议对bcossdk的一次接口调用，就用一个单独的CallbackFuture,不要混用
# 否则sdk并发时，回调的消息会复用callback入口,导致返回的消息不对应刚才发送的req,或者需要用消息唯一序列号来对应是哪个请求包
# 所以，一次调用一个future，基本能保证返回的消息，对应的是发送的消息，代码读起来也比较简单
# todo: 可以扩展一些特性，比如，收到sdk回调后，立刻再递归回调应用层设置的callback，
# 在event监听场景比较有意义，目前先统一用wait，参见tests/testbcos3event.py

class BcosCallbackFuture:
    response_queue = None
    context: BcosReqContext = None
 
    
    def __init__(self, context_name=None, context_msg=None):
        self.response_queue = queue.Queue(1)
        if context_name is not None or context_msg is not None:
            self.context = BcosReqContext(self.next_seq(), context_name, context_msg)
        
        self.callback = BCOS_CALLBACK_FUNC(self.bcos_callback)
        # print(f"when INIT {context_name}:{self.callback}:Queue:{self.response_queue}{self.context.detail()}")
        self.amop_callback = BCOS_AMOP_SUB_CALLBACK_FUNC(self.bcos_amop_callback)
        self.amop_publish_callback = BCOS_AMOP_PUBLISH_CALLBACK_FUNC(self.bcos_amop_publish_callback)
    
    def next_seq(self, inc=1):
        global G_SEQ
        G_SEQ = G_SEQ + inc
        return G_SEQ
    
    def is_empty(self):
        return self.response_queue.empty()
    
    def bcos_callback(self, c_resp):
        if c_resp is None:
            return
        
        resp = BcosResponse(c_resp)
        
        #if(resp.context is not None):
        #    print(f"when CALLBACK : {self.context.name},self seq:{self.context.seq}, response seq {resp.context.detail()}")
        self.response_queue.put_nowait(resp)
        # print(f"--->QSIZE::{self.queue.qsize()}------<<<<",)
    
    def bcos_amop_callback(self, endpoint, seq, c_resp):
        # print("[wrap]bcos_sdk_c_amop_subscribe_cb callback")
        
        if c_resp is None:
            return

        resp = BcosResponse(c_resp)
        resp.endpoint = str(endpoint, "utf-8")
        resp.seq = str(seq, "utf-8")
        self.response_queue.put_nowait(resp)
    
    def bcos_amop_publish_callback(self, c_resp):
    
        if c_resp is None:
            return
        # print("amop_publish_callback")
        resp = BcosResponse(c_resp)
        # print(self.error, self.desc)
        self.response_queue.put_nowait(resp)
    
    def wait(self, timeout=5)->(int,BcosResponse):
        is_timeout = False
        resp = None
        try:
            #self.is_timeout = False
            resp =  self.response_queue.get(True, timeout)
        except:
            is_timeout = True
            pass
        return (is_timeout,resp)
    
    def display(self):
        print(self.detail())
        
    def detail(self):
        s = f"queuesize:{self.response_queue.qsize()}"
        if self.context is not None:
            s += f"reqcontext:{self.context.detail()}"
        return s

