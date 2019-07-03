'''
  bcosliteclientpy is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/FISCO-BCOS)
  bcosliteclientpy is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Free Software Foundation
  This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE
  Thanks for authors and contributors of eth-abi，eth-account，eth-hash，eth-keys，eth-typing，eth-utils，rlp, eth-rlp , hexbytes ...and relative projects
  @author: kentzhang
  @date: 2019-06
'''

from client.bcosclient import (
    BcosClient,
    BcosError
)
import os
from eth_utils import to_checksum_address
from client.datatype_parser import DatatypeParser

client = BcosClient()
info = client.init()
print(info)


#从文件加载abi定义
abi_file  ="contracts/SimpleInfo.abi"
data_parser = DatatypeParser()
data_parser.load_abi_file(abi_file)
contract_abi = data_parser.contract_abi

#以下是查询类的接口，大部分是返回json，可以根据对fisco bcos rpc接口json格式的理解，进行字段获取和转码
'''
useful helper:
int(num,16)  hex -> int
hex(num)  : int -> hex
'''

doQueryTest =True
if doQueryTest:
    print("\n>>---------------------------------------------------------------------")
    res = client.getNodeVersion()
    print("\n>>---------------------------------------------------------------------")
    print("getClientVersion",res)
    print("\n>>---------------------------------------------------------------------")
    try:
        res = client.getBlockNumber()
        print("getBlockNumber",res)
    except BcosError as e:
        print("bcos client error,",e.info())
    print("\n>>---------------------------------------------------------------------")
    print("getPeers",client.getPeers())
    print("\n>>---------------------------------------------------------------------")
    print("getBlockByNumber",client.getBlockByNumber(1))
    print("\n>>---------------------------------------------------------------------")
    print("getBlockHashByNumber",client.getBlockHashByNumber(1))
    print("\n>>---------------------------------------------------------------------")
    print("getBlockByHash",client.getBlockByHash("0xe7588bf4ee5a6fb5aae9bdcc2c4f3c58cf7a789b15a4daa6617ed594b5ba3951"))
    print("\n>>---------------------------------------------------------------------")
    print("getTransactionByHash",client.getTransactionByHash("0x41fa9a0ce36d486ee2bf6d2219b68b44ca300ec7aeb07f8f2aa9c225655d2b61"))
    print("\n>>---------------------------------------------------------------------")
    print("getTransactionByBlockHashAndIndex",client.getTransactionByBlockHashAndIndex("0xe7588bf4ee5a6fb5aae9bdcc2c4f3c58cf7a789b15a4daa6617ed594b5ba3951",0))
    print("\n>>---------------------------------------------------------------------")
    print("getTransactionByBlockNumberAndIndex",client.getTransactionByBlockNumberAndIndex(1,0))
    print("\n>>---------------------------------------------------------------------")
    print("getTransactionReceipt",client.getTransactionReceipt("0x41fa9a0ce36d486ee2bf6d2219b68b44ca300ec7aeb07f8f2aa9c225655d2b61"))
    print("\n>>---------------------------------------------------------------------")
    print("getPendingTransactions",client.getPendingTransactions())
    print("\n>>---------------------------------------------------------------------")
    print("getPendingTxSize",client.getPendingTxSize())
    print("\n>>---------------------------------------------------------------------")
    print("getCode",client.getCode("0x83592a3cf1af302612756b8687c8dc7935c0ad1d"))
    print("\n>>---------------------------------------------------------------------")
    print("getTotalTransactionCount",client.getTotalTransactionCount())
    print("\n>>---------------------------------------------------------------------")
    print("getSystemConfigByKey",client.getSystemConfigByKey("tx_count_limit"))
    print("\n>>---------------------------------------------------------------------")

    print("getPbftView",int(client.getPbftView(),16))
    print("\n>>---------------------------------------------------------------------")
    print("getSealerList",client.getSealerList())
    print("\n>>---------------------------------------------------------------------")
    print("getObserverList",client.getObserverList())
    print("\n>>---------------------------------------------------------------------")
    print("getConsensusStatus",client.getConsensusStatus())
    print("\n>>---------------------------------------------------------------------")
    print("getSyncStatus",client.getSyncStatus())
    print("\n>>---------------------------------------------------------------------")
    print("getGroupPeers",client.getGroupPeers())
    print("\n>>---------------------------------------------------------------------")
    print("getNodeIDList",client.getNodeIDList())
    print("\n>>---------------------------------------------------------------------")
    print("getGroupList",client.getGroupList())
