'''
  bcosliteclientpy is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/)
  bcosliteclientpy is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Free Software Foundation
  This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE
  Thanks for authors and contributors of eth-abi，eth-account，eth-hash，eth-keys，eth-typing，eth-utils，rlp, eth-rlp , hexbytes ...and relative projects
  @author: kentzhang
  @date: 2019-06
'''

'''
channel protocal ref: 
https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/design/protocol_description.html#channelmessage
'''

import ssl
import socket
from client.channelpack import ChannelPack
from client.stattool import  StatTool
from utils.encoding import (
    FriendlyJsonSerde)
from client.bcoserror import BcosError
from eth_utils import (
    to_dict,
    to_text,
    to_bytes,
)
import itertools
import uuid
import json
import time
import traceback
from queue import Empty

class ChannelHandler:
    context = None
    CA_File= None
    node_crt_file= None
    node_key_file=None
    ECDH_curve = "secp256k1"
    ssock = None
    host = None
    port = None
    request_counter = itertools.count()
    logger = None
    recvThread = None
    sendThread = None


    def initTLSContext(self,ca_file,node_crt_file,node_key_file,
                       protocal=ssl.PROTOCOL_TLSv1_2,
                       verify_mode=ssl.CERT_REQUIRED):
        context = ssl.SSLContext(protocal)
        context.check_hostname = False
        context.load_verify_locations(ca_file)
        context.load_cert_chain(node_crt_file, node_key_file)
        #print(context.get_ca_certs())
        context.set_ecdh_curve(self.ECDH_curve)
        context.verify_mode = verify_mode
        self.context = context

    def finish(self):
        self.ssock.shutdown(socket.SHUT_RDWR)
        self.ssock.close()
        self.ssock = None
        self.recvThread.finish()
        self.recvThread.join(timeout=2)
        self.sendThread.finish()
        self.sendThread.join(timeout=2)



    def start(self, host, port):
        self.host=host
        self.port=port
        sock = socket.create_connection((host, port))
        self.logger.debug("connect {}:{},as socket {}".format(host, port, sock))
            # 将socket打包成SSL socket
        ssock = self.context.wrap_socket(sock)
        self.ssock = ssock
        self.recvThread =ChannelRecvThread(self)
        self.recvThread.start()
        self.sendThread = ChannelSendThread(self)
        self.sendThread.start()

    def decode_rpc_response(self, response):
        text_response = to_text(response)
        return FriendlyJsonSerde().json_decode(text_response)

    def encode_rpc_request(self, method, params):
        rpc_dict = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": next(self.request_counter),
        }
        encoded = FriendlyJsonSerde().json_encode(rpc_dict)
        return to_bytes(text=encoded)

    '''
    result:
    0	成功
    100	节点不可达
    101	SDK不可达
    102	超时
    '''
    errorMsg = dict()
    errorMsg[0]="success"
    errorMsg[100]="node unreachable"
    errorMsg[101]="sdk unreachable"
    errorMsg[102]="timeout"


    def make_request(self, method, params, type=ChannelPack.TYPE_RPC):
        stat = StatTool.begin()
        rpc_data = self.encode_rpc_request(method,params)
        self.logger.debug("request rpc_data : {}".format(rpc_data) )
        #print("request rpc_data", rpc_data)
        request_pack   = ChannelPack(type,ChannelPack.make_seq32(), 0,rpc_data)

        res = self.send_pack(request_pack)
        starttime = time.time()
        responsematch = False
        while time.time() - starttime < 10: # spend max 10 sec to wait a correct response
            try:
                theQueue = self.recvThread.getQueue(ChannelPack.TYPE_RPC)
                responsepack = theQueue.get(block=True, timeout=3) # pop msg from queue
            except Empty as e:
                continue
            #print("got a pack from queue, detail:{}".format(responsepack.detail()))
            self.logger.debug("got a pack from queue, detail:{}".format(responsepack.detail()))
            if responsepack.type == ChannelPack.TYPE_RPC and responsepack.seq == request_pack.seq:
                responsematch = True
                break
            else:
                #print("*******SKIP!!!! pack ", responsepack.detail())
                self.logger.debug("*******SKIP!!!! pack {}".format( responsepack.detail() ))
                responsepack = None
                continue
        if responsematch == False:
            raise  BcosError(102,None,"timeout")

        result = responsepack.result
        data = responsepack.data.decode("utf-8")

        msg = "success"
        if(result!=0):
            if result in self.errorMsg:
                msg = "unknow error %d"%result
                msg = self.errorMsg[result]
            raise BcosError(result,msg)
        response =  FriendlyJsonSerde().json_decode(data)
        stat.done()
        stat.debug("make_request:{}".format(method) )
        self.logger.debug("GetResponse. %s, Response: %s",
                           method, response)
        #print("response from server:",response)
        self.logger.debug("response from server: {}".format( response) )
        if "result" not in response:
            tempresp =dict()
            tempresp["result"] = response
            response =tempresp
        return response


    def send_pack(self,pack):
        if self.sendThread.packQueue.full():
            self.logger.error("channel send Queue full!")
            raise BcosError(-1,None,"channel send Queue full!")
        self.sendThread.packQueue.put(pack)


#--------------------------------------------------------------------
#--------------------------------------------------------------------
# thread: channel reading
#--------------------------------------------------------------------
#--------------------------------------------------------------------

import threading
import queue
class ChannelRecvThread(threading.Thread):
    QUEUE_SIZE = 1024
    channelHandler = None
    queueMapping = dict()
    keepWorking = True
    threadLock = threading.RLock()
    logger = None

    def getQueue(self,type):
        if type in self.queueMapping:
            return self.queueMapping[type]
        self.queueMapping[type] = queue.Queue(ChannelRecvThread.QUEUE_SIZE)
        return self.queueMapping[type]

    def __init__(self, handler,name="ChannelRecvThread" ):
        threading.Thread.__init__(self)
        #self.threadID = threadID
        self.name = name
        self.channelHandler = handler
        self.logger = handler.logger

    respbuffer = bytearray() #a buffer append by read, consume by decode

    def read_channel(self):
        # 接收服务端返回的信息
        try:
            #print("channelHandler.ssock.recv begin.")
            self.logger.debug("{} channelHandler.ssock.recv begin.".format(self.name))
            msg = self.channelHandler.ssock.recv(1024 * 10)
            #print("channelHandler.ssock.recv len:{},{}".format(len(msg),msg))
            self.logger.debug("channelHandler.ssock.recv len:{},{}".format(len(msg),msg))
            if msg == None:
                return -1
            if len(msg)==0:
                return 0
        except Exception as e:
            self.logger.error ("{}:ssock read error {}".format(self.name,e))
            return -1
        self.respbuffer += msg
        #if no enough data even for header ,continue to read
        if len(self.respbuffer) < ChannelPack.getheaderlen():
            return len(msg)

        code = 0
        #decode all packs in buffer from node,maybe got N packs on one read
        while code!=-1:  #-1 means no enough bytes for decode, should break to  continue read and wait
            (code, decodelen, responsePack) = ChannelPack.unpack(bytes(self.respbuffer))
            if decodelen > 0:
                self.respbuffer = self.respbuffer[decodelen:] #cut the buffer from last decode  pos
            if code!=-1 and responsePack!=None: #got a pack
                #print("get a pack from node, put to queue {}".format(responsePack.detail()))
                theQueue = self.getQueue(responsePack.type)
                self.logger.debug("{}:pack from node, put queue(qsize{}),detail {}".format(self.name,theQueue.qsize(), responsePack.detail()))
                if theQueue.full():
                    theQueue.get() #if queue full ,pop the head item ,!! the item LOST
                    self.logger.error("{}:queue {} FULL pop and LOST: {}".format(self.name,responsePack.type,responsePack.detail()))
                theQueue.put(responsePack)
                #self.print_queue()

        return len(msg)

    def print_queue(self):
        print("queue types ",self.queueMapping.items())
        for (type,q) in self.queueMapping.items():
            print("queue type {},size {}".format(hex(type),q.qsize()))

    def finish(self):
        self.keepWorking = False

    def run(self):
        lockres = ChannelRecvThread.threadLock.acquire(blocking=False)
        if(lockres == False ): #other thread has got the lock and running
            #print(self.name+":other thread has got the lock and running ")
            self.logger.error(self.name+":other thread has got the lock and running ")
            return
        try:
            self.keepWorking = True
            self.logger.debug(self.name+":start thread-->")
            while self.keepWorking:
                bytesread = self.read_channel()
                if self.keepWorking == False:
                    break
                if bytesread == 0: #if async read, maybe return 0
                    time.sleep(0.1)
                if bytesread < 0: #error accord when read
                    time.sleep(1)
        except Exception as e:
            self.logger.error("{} recv error {}".format(self.name,e))

        finally:
            self.logger.debug("{}:thread finished ,keepWorking = {}".format(self.name,self.keepWorking))
            ChannelRecvThread.threadLock.release()

#-----------------------------------------------------------
#-----------------------------------------------------------
# send thread begin
#-----------------------------------------------------------
#-----------------------------------------------------------

class ChannelSendThread(threading.Thread):
    QUEUE_SIZE = 1024
    channelHandler = None
    packQueue =None
    keepWorking = True
    threadLock = threading.RLock()
    heatbeatStamp = 3 # heatbeat very N sec
    logger = None

    def sendpack(self,pack):
        if self.packQueue.full():
            raise BcosError(-1,None,"sendThread Queue full")
        self.packQueue.put(pack)

    def __init__(self,handler,name="ChannelSendThread"):
        threading.Thread.__init__(self)
        self.name = "channelSendThread"
        self.channelHandler = handler
        self.packQueue =  queue.Queue(ChannelSendThread.QUEUE_SIZE)
        self.logger = handler.logger

    lastheatbeattime = time.time()
    def check_heatbeat(self):
        if time.time() - self.lastheatbeattime < self.heatbeatStamp:
            return
        pack = ChannelPack(ChannelPack.TYPE_HEATBEAT, ChannelPack.make_seq32(), 0, bytes("", "utf-8"))
        self.sendpack(pack)
        self.lastheatbeattime = time.time()

    def finish(self):
        self.keepWorking = False

    def run(self):
        lockres = ChannelSendThread.threadLock.acquire(blocking=False)
        if(lockres == False ): #other thread has got the lock and running
            print(self.name+":other thread has got the lock and running ")
            return
        try:
            self.keepWorking = True
            self.logger.debug(self.name+":start thread-->")
            while self.keepWorking:
                try:
                    pack = self.packQueue.get(block=True,timeout=0.2)
                except Empty as e:
                    self.check_heatbeat()
                    continue
                self.lastheatbeattime = time.time() #reset heatbeat time
                self.logger.debug("{} send pack {}".format(self.name,pack.detail()))
                #print("{} send pack {}".format(self.name,pack.detail()))
                buffer = pack.pack()
                try:
                    res = self.channelHandler.ssock.send(buffer)
                    if res < 0:
                        self.logger.error("{}:ssock send error {}".format(self.name,res))
                except Exception as e:
                    self.logger.error("{}:ssock send error {}".format(self.name, e))

        except Exception as e:
            self.logger.error("{}:ssock send error {}".format(self.name,e))
            #self.logger.error(traceback.format_exc())
        finally:
            self.logger.debug("{}:thread finished ,keepWorking = {}".format(self.name,self.keepWorking))
            ChannelSendThread.threadLock.release()

