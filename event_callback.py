#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
  bcosliteclientpy is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/)
  bcosliteclientpy is free software: you can redistribute it and/or modify it under the
  terms of the MIT License as published by the Free Software Foundation. This project is
  distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Thanks for
  authors and contributors of eth-abi, eth-account, eth-hash，eth-keys, eth-typing, eth-utils,
  rlp, eth-rlp , hexbytes ... and relative projects
  @author: kentzhang
  @date: 2019-06
'''
import sys
from client.bcosclient import BcosClient
import os
from client_config import client_config
from client.stattool import StatTool
from client.datatype_parser import DatatypeParser
from client.common.compiler import Compiler
from client_config import client_config
from client.bcoserror import BcosException, BcosError
from client.contractnote import ContractNote
from eth_utils import encode_hex,decode_hex
import uuid
from eth_utils.crypto import  keccak
import json
import struct
from utils.encoding import FriendlyJsonSerde
from client.bcoserror import BcosError, ChannelException
from eth_utils import (to_text, to_bytes)
from client.channel_push_dispatcher import ChannelPushHandler
from client.channelpack import ChannelPack


def usage():
    usagetext = "params: [contractname] [address(last)] [event_name] [indexed value]\n"
    usagetext = usagetext+"eg: for contract sample [contracts/HelloEvent.sol], use:\n"
    usagetext = usagetext+"python event_callback HelloEvent last on_set \n"
    usagetext = usagetext+"python event_callback HelloEvent last on_number 5\n...(and other events)"
    print(usagetext)


class EventPushHandler(ChannelPushHandler):
    parser = DatatypeParser()
    def on_push(self,packmsg:ChannelPack):
        print("EventPushHandler",packmsg.detail())
        strmsg = packmsg.data.decode("utf-8")
        response = json.loads( strmsg )
        loglist = parser.parse_event_logs(response["logs"])
        print(json.dumps(loglist,indent=4))

parser :DatatypeParser= None
client :BcosClient= None
eventHandler = EventPushHandler()

def format_event_register_request(from_block,to_block,addresses,topics,groupid = "1",filterid= None):
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
    if filterid == None:
        seq = uuid.uuid1()
        filterid = seq.hex
    request["filterID"] = filterid
    requestJson = FriendlyJsonSerde().json_encode(request)
    return requestJson

def register_event_callback(addresses,event_name,indexed_value):
    topics = []
    topic0 = parser.topic_from_event_name(event_name)
    topics.append(topic0)
    event_abi = parser.event_name_map[event_name]
    print(event_abi)
    if len(indexed_value) > 0:
        indexedinput=[]
        for input in event_abi["inputs"]:
            if input["indexed"] is True:
                indexedinput.append((input['name'] ,input['type']) )
        print(indexedinput)
        i = 0
        for v in indexed_value:
            print(v)
            itype = indexedinput[i][1]
            topic = None
            if itype.startswith('int'):
                topic = DatatypeParser.topic_from_int(v)
            if type == 'string':
                topic = DatatypeParser.topic_from_string(v)
            if type == 'address':
                topic = DatatypeParser.topic_from_address(v)
            if type == 'boolean':
                topic = DatatypeParser.topic_from_boolean(v)
            if not (topic is None):
                topics.append(topic)
            i = i+1
    requestJson = format_event_register_request("latest","latest",addresses,topics)
    requestbytes  = ChannelPack.pack_amop_topic_message("",requestJson)
    client.channel_handler.pushDispacher.add_handler(ChannelPack.EVENT_LOG_PUSH,eventHandler)
    response =  client.channel_handler.make_channel_request(requestbytes,
                                                            ChannelPack.CLIENT_REGISTER_EVENT_LOG,
                                                            ChannelPack.CLIENT_REGISTER_EVENT_LOG)
    (topic,result) = ChannelPack.unpack_amop_topic_message(response)
    dataobj = json.loads(result)
    print("after register ,event_name:{},topic:{},result:{}".format(event_name,topic,dataobj['result']))

# abi address event_name  indexed_value
def main(argv):
    global parser
    global client
    if len(argv) < 3:
        usage()
        exit(0)

    contractname = argv[0]
    address = argv[1]
    event_name = argv[2]
    indexed_value = argv[3:]

    print("usage input {},{},{},{}".format(contractname,address,event_name,indexed_value))
    if address == "last":
        cn = ContractNote()
        address = cn.get_last(contractname)
        print("hex address :",address)
    abifile = "contracts/"+contractname+".abi"
    parser = DatatypeParser(abifile)
    client = BcosClient()
    print(client.getinfo())
    register_event_callback([address],event_name,indexed_value)

if __name__ == "__main__":
    main(sys.argv[1:])