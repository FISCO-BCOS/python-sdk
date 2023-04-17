'''
typedef void (*bcos_sdk_c_amop_subscribe_cb)(const char* endpoint, const char* seq, struct bcos_sdk_c_struct_response* resp);
typedef void (*bcos_sdk_c_amop_publish_cb)(struct bcos_sdk_c_struct_response* resp);

void bcos_amop_subscribe_topic(void* sdk, char** topics, size_t count);
void bcos_amop_subscribe_topic_with_cb(void* sdk, const char* topic, bcos_sdk_c_amop_subscribe_cb cb, void* context);
void bcos_amop_set_subscribe_topic_cb(void* sdk, bcos_sdk_c_amop_subscribe_cb cb, void* context);
void bcos_amop_unsubscribe_topic(void* sdk, char** topics, size_t count);
void bcos_amop_publish(void* sdk, const char* topic, void* data, size_t size, uint32_t timeout,bcos_sdk_c_amop_publish_cb cb, void* context);
void bcos_amop_broadcast(void* sdk, const char* topic, void* data, size_t size);
void bcos_amop_send_response(void* sdk, const char* peer, const char* seq, void* data, size_t size)；
'''
import sys
sys.path.append("./")

from bcos3sdk.bcos3callbackfuture import BcosCallbackFuture
from bcos3sdk.bcos3datadef import *


import time
from ctypes import POINTER




from bcos3sdk.bcos3client import Bcos3Client


bcos3client = Bcos3Client()
print(bcos3client.getinfo())
num = bcos3client.getBlockNumber()
testtopic = "test123"
print(f"Current block number {num}")

def bcos_amop_subscribe_cb(a, b, r:POINTER(BcosResponseCType)):
    print("py callback",a,b,r)
    resp = BcosResponse(r)
    print(resp.detail())


def bcos_amop_publish_cb_simple(r:POINTER(BcosResponseCType)):
    print("py callback bcos_amop_subscribe_cb_simple",r)
    pass

publishcb =BCOS_AMOP_PUBLISH_CALLBACK_FUNC( bcos_amop_publish_cb_simple )
subcb = BCOS_AMOP_SUB_CALLBACK_FUNC( bcos_amop_subscribe_cb)


def amop_sub():
    topiclist=[testtopic,"test888"]
    bcos3client.amop_subscribe(topiclist)
    cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
    bcos3client.amop_set_subscribe_topic_cb(0,0)
    print(bcos_amop_subscribe_cb)
    bcos3client.amop_set_subscribe_topic_cb(bcos_amop_subscribe_cb, 0)
    e = bcos3client.get_last_error_full()
    print("set callback ",e)
    waittick = 0
    lasttick = time.time()
    n = 0
    while True:
        #cbfuture.display()
        n=n+1
        time.sleep(3)
        print(n)
    
def amop_sub_cb():
    topics=testtopic
    cbfuture = bcos3client.amop_subscribe_with_cb(topics)
    res = bcos3client.get_last_error_full()
    
    print(f"subscribe msg {res}")
    waittick = 0
    lasttick = time.time()
    n = 0
    while True:
        n = n+1
        #cbfuture.display()
        (is_timeout,resp) = cbfuture.wait()
        if is_timeout is False:  # default timeout 5 sec
            print(f">>> CBFuture Get Message : {resp.data}, peer:{resp.endpoint},seq:{resp.seq} ")
            bcos3client.amop_send_response(resp.endpoint,resp.seq,"GOT:"+resp.data)
        else:
            print(f">>> CBFuture  timeout ,try again")
        
        nowtick = time.time()
        if nowtick - lasttick > 3:
            waittick = waittick + 1
            print(f"WaitTick : {waittick}")
            lasttick = time.time()
        
        if waittick >= 50:
            break


def amop_broadcast(data):
    bcos3client.amop_broadcast(testtopic, "1")
    res = bcos3client.get_last_error_full()
    print(f"broadcast res {res}")
    
    
def amop_publish(data):
    n = 0
    cbfuture = None
    for n in range(0,10):
        newdata = f"{data} : {n}"
        cbfuture = bcos3client.amop_publish(testtopic,newdata,future=cbfuture)
        (is_timeout,resp) = cbfuture.wait()
        #cbfuture.display()
        if is_timeout:
            break
        print("response: ",resp.detail())
    
    


if __name__ == "__main__":
    cmd = sys.argv[1]
    print("cmd = ",cmd)

    cbfuture = BcosCallbackFuture()
 
    if cmd == "sub":
        amop_sub()
    if cmd == "subcb":
        amop_sub_cb()
    else:
        #amop_broadcast(cmd)
        amop_publish(cmd)
    