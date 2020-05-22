#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
  FISCO BCOS/Python-SDK is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/)
  FISCO BCOS/Python-SDK is free software: you can redistribute it and/or modify it under the
  terms of the MIT License as published by the Free Software Foundation. This project is
  distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Thanks for
  authors and contributors of eth-abi, eth-account, eth-hash，eth-keys, eth-typing, eth-utils,
  rlp, eth-rlp , hexbytes ... and relative projects
  @author: kentzhang
  @date: 2019-06
'''

from client.bcosclient import BcosClient
from client.datatype_parser import DatatypeParser
import uuid
import json
import threading
from utils.encoding import FriendlyJsonSerde
from client.channelpack import ChannelPack
from client.channel_push_dispatcher import ChannelPushHandler
class EventCallbackHandler:
    def on_event(self,eventdata):
        pass

class EventCallbackManager(ChannelPushHandler):
    abiparser: DatatypeParser = None
    callback_register = dict()
    lock = threading.RLock()
    def set_callback(self,filterid,callback):
        try:
            self.lock.acquire()
            #print("set callbackup ",filterid,callback)
            self.callback_register[filterid] = callback
        except Exception as e:
            self.logger.error("channel push dispatcher add handler error", e)
        finally:
            self.lock.release()

    def remove_callback(self,filterid,callback):
        try:
            self.lock.acquire()
            if not filterid in self.callback_register:
                return
            else:
                self.callback_register.pop(filterid)
        except Exception as e:
            self.logger.error("channel push dispatcher add handler error", e)
        finally:
            self.lock.release()

    def get_callback(self,filterid):
        if filterid in self.callback_register:
            return self.callback_register[filterid]
        else:
            return None

    def on_push(self, packmsg: ChannelPack):
        #print("--------------------EventPushHandler: type {},result:{},len:{}".format(
        #    hex(packmsg.type), packmsg.result, packmsg.totallen))
        if packmsg.type != ChannelPack.EVENT_LOG_PUSH:
            print("WRONG TYPE:-EventPushHandler: type {},result:{},len:{}".format(
                  hex(packmsg.type), packmsg.result, packmsg.totallen))
            return
        strmsg = packmsg.data.decode("utf-8")
        eventdata = json.loads(strmsg)
        filterid = eventdata["filterID"]

        #print("filterid",filterid)
        eventcallback = self.get_callback(filterid)
        #print(eventcallback)
        if eventcallback is None:
            return
        eventcallback.on_event(eventdata)

class BcosEventCallback:
    client: BcosClient = None
    ecb_manager = EventCallbackManager()
    def format_event_register_request(
            self,
            from_block,
            to_block,
            addresses,
            topics,
            groupid,
            filterid):
        '''
        {
      "fromBlock": "latest",
      "toBlock": "latest",
      "addresses": [
        0xca5ed56862869c25da0bdf186e634aac6c6361ee
      ],
      "topics": [
        "0x91c95f04198617c60eaf2180fbca88fc192db379657df0e412a9f7dd4ebbe95d"
      ],
      "groupID": "1",
      "filterID": "bb31e4ec086c48e18f21cb994e2e5967"
    }'''
        request = dict()
        request["fromBlock"] = from_block
        request["toBlock"] = to_block
        request["addresses"] = addresses
        request["topics"] = topics
        request["groupID"] = groupid
        request["filterID"] = filterid
        requestJson = FriendlyJsonSerde().json_encode(request)
        return requestJson


    def setclient(self,client):
        self.client = client
        self.add_channel_push_handler(self.ecb_manager)

    def add_channel_push_handler(self, eventHandler):
        self.client.channel_handler.pushDispacher.add_handler(
            ChannelPack.EVENT_LOG_PUSH, eventHandler)

    def register_eventlog_filter(self, eventcallback,abiparser ,addresses, event_name, indexed_value=None,
                                fromblock="latest", to_block="latest"):
        topics = []
        if event_name is not None:
            topic0 = abiparser.topic_from_event_name(event_name)
            topics.append(topic0)
            event_abi = abiparser.event_name_map[event_name]
        #print("event abi:", event_abi)
        if indexed_value is not None and len(indexed_value) > 0:
            indexedinput = []
            for input in event_abi["inputs"]:
                if input["indexed"] is True:
                    indexedinput.append((input['name'], input['type']))
            # print(indexedinput)
            i = 0
            for v in indexed_value:
                itype = indexedinput[i][1]
                topic = DatatypeParser.topic_from_type(itype, v)
                if not (topic is None):
                    topics.append(topic)
                i = i + 1
        #create new filterid by uuid
        seq = uuid.uuid1()
        filterid = seq.hex
        requestJson = self.format_event_register_request(fromblock, to_block, addresses, topics,self.client.groupid,filterid)
        requestbytes = ChannelPack.pack_amop_topic_message("", requestJson)
        response = self.client.channel_handler.make_channel_request(
            requestbytes, ChannelPack.CLIENT_REGISTER_EVENT_LOG, ChannelPack.CLIENT_REGISTER_EVENT_LOG)
        (topic, result) = ChannelPack.unpack_amop_topic_message(response)
        dataobj = json.loads(result)
       # print(dataobj)
        if dataobj["result"] is 0:
            self.ecb_manager.set_callback(filterid,eventcallback)
        return dataobj
