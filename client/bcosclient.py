'''
  bcosliteclientpy is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/)
  bcosliteclientpy is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Free Software Foundation
  This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE
  Thanks for authors and contributors of eth-abi，eth-account，eth-hash，eth-keys，eth-typing，eth-utils，rlp, eth-rlp , hexbytes ...and relative projects
  @author: kentzhang
  @date: 2019-06
'''

#reference :https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html
'''
useful helper:
int(num,16)  hex -> int
hex(num)  : int -> hex
'''

import rlp
from utils.contracts import (
    encode_transaction_data,

)
from client.stattool import  StatTool
from client import clientlogger
from utils.contracts import get_function_info
from utils.abi import *
from eth_abi import encode_single, encode_abi,decode_single,decode_abi
from eth_utils.hexadecimal import decode_hex,encode_hex
from client_config import  client_config
import sys
import json
import utils.rpc
import time
import logging

from eth_account.account import (
    Account
)
from eth_utils.hexadecimal import decode_hex, encode_hex

class BcosError(Exception):
    code = None
    data = None
    message = None
    def __init__(self, c,d,m):
        self.code = c
        self.data = d
        self.message = m
    def info(self):
        return "code :{},data :{},message : {}".format(self.code, self.data, self.message)

#-----------------------------------------------------------------------------------------------------
class BcosClient:
    client_account = None
    rpc = None
    fiscoChainId = None
    groupid = None
    logger =clientlogger.logger #logging.getLogger("BcosClient")

    def __init__(self):
        self.init()

    def init(self):
        #load the account from keyfile
        if(client_config.account_keyfile!=None):
            self.fiscoChainId = client_config.fiscoChainId
            self.groupid = client_config.groupid
            keystorefile = client_config.account_keyfile_path+"/"+client_config.account_keyfile
            with open(keystorefile, "r") as dump_f:
                keytext = json.load(dump_f)
                privkey = Account.decrypt(keytext, client_config.account_password)
                self.client_account = Account.from_key(privkey)
        if(client_config.remote_rpcurl!=None):
            self.rpc = utils.rpc.HTTPProvider(client_config.remote_rpcurl)
            self.rpc.logger=self.logger
        return self.getinfo()
    '''{  "error": {
        "code": 7,
        "data": null,
        "message": "Only pbft consensus supports the view property"
      },  "id": 1,  "jsonrpc": "2.0"
    }'''

    def getinfo(self):
        info = "url:{}\n".format(client_config.remote_rpcurl)
        info = "rpc:{}\n".format(self.rpc)
        info += "account address: {}\n".format(self.client_account.address)
        info += "groupid :{}\n".format(self.groupid)
        return info


    def is_error_reponse(self,response):
        if response == None:
            e = BcosError(-1, None, "response is None")
            return e
        if("error" in response):
            msg = response["error"]["message"]
            code = response["error"]["code"]
            data = None
            if("data" in response["error"]):
                data = response["error"]["data"]
            self.logger.error("is_error_reponse code: {}, msg:{} ,data:{}".format(code,msg,data) )
            e = BcosError(code,data,msg)
            return e
        return None

    def common_request(self,cmd,params):
        stat = StatTool.begin()
        response = self.rpc.make_request(cmd, params)
        error = self.is_error_reponse(response)
        memo  ="DONE"
        if(error!=None):
            memo = "ERROR {}:{}".format(error.code,error.message)
        stat.done()
        stat.debug("commonrequest:{}:{}".format(cmd,memo))

        if(error!=None):
            raise error;
        return response["result"]

    '''
    // Request
curl -X POST --data '{"jsonrpc":"2.0","method":"getClientVersion","params":[],"id":1}' http://127.0.0.1:8545 |jq
// Result
{
  "id": 83,
  "jsonrpc": "2.0",
  "result": {
    "Build Time": "20190106 20:49:10",
    "Build Type": "Linux/g++/RelWithDebInfo",
    "FISCO-BCOS Version": "2.0.0",
    "Git Branch": "master",
    "Git Commit Hash": "693a709ddab39965d9c39da0104836cfb4a72054"
  }
}    '''
    def  getNodeVersion(self):
        cmd = "getClientVersion"
        params= []
        return self.common_request(cmd,params)

  # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getblocknumber
    def getBlockNumber(self):
        cmd = "getBlockNumber"
        params= [self.groupid]
        num_hex =  self.common_request(cmd, params)
        return int(num_hex,16)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getpbftview
    def getPbftView(self):
        cmd = "getPbftView"
        params= [self.groupid]
        return  self.common_request(cmd, params)


    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getsealerlist
    def getSealerList(self):
        cmd = "getSealerList"
        params= [self.groupid]
        return  self.common_request(cmd, params)
    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getobserverlist

    def getObserverList(self):
        cmd = "getObserverList"
        params= [self.groupid]
        return  self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getconsensusstatus
    def getConsensusStatus(self):
        cmd = "getConsensusStatus"
        params= [self.groupid]
        return  self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getsyncstatus
    def getSyncStatus(self):
        cmd = "getSyncStatus"
        params= [self.groupid]
        return  self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getpeers
    def getPeers(self):
        cmd="getPeers"
        params = [self.groupid]
        return self.common_request(cmd,params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getgrouppeers
    def getGroupPeers(self):
        cmd = "getGroupPeers"
        params= [self.groupid]
        return  self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getnodeidlist
    def getNodeIDList(self):
        cmd = "getNodeIDList"
        params= [self.groupid]
        return  self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getgrouplist
    def getGroupList(self):
        cmd = "getGroupList"
        params= [self.groupid]
        return  self.common_request(cmd, params)


    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getblockbyhash
    def getBlockByHash(self,hash,includeTransactions=False):
        cmd = "getBlockByHash"
        params = [self.groupid,hash,includeTransactions]
        return self.common_request(cmd, params)
    #https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getblockbynumber
    def getBlockByNumber(self,num,includeTransactions=False):
        cmd = "getBlockByNumber"
        params = [self.groupid,hex(num),includeTransactions]
        return self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getblockhashbynumber
    def getBlockHashByNumber(self,num):
        cmd = "getBlockHashByNumber"
        params = [self.groupid,hex(num)]
        return self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_cn/release-2.0/docs/api.html#gettransactionbyhash
    def getTransactionByHash(self,hash):
        cmd = "getTransactionByHash"
        params = [self.groupid,hash]
        return self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#gettransactionbyblockhashandindex
    def getTransactionByBlockHashAndIndex(self,hash,index):
        cmd = "getTransactionByBlockHashAndIndex"
        params = [self.groupid,hash,hex(index)]
        return self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#gettransactionbyblocknumberandindex
    def getTransactionByBlockNumberAndIndex(self,num,index):
        cmd = "getTransactionByBlockNumberAndIndex"
        params = [self.groupid,hex(num),hex(index)]
        return self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#gettransactionreceipt
    def getTransactionReceipt(self,hash):
        cmd = "getTransactionReceipt"
        params = [self.groupid,hash]
        return self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getpendingtransactions
    def getPendingTransactions(self):
        cmd = "getPendingTransactions"
        params = [self.groupid]
        return self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getpendingtxsize
    def getPendingTxSize(self):
        cmd = "getPendingTxSize"
        params = [self.groupid]
        return self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getcode
    def getCode(self,address):
        cmd = "getCode"
        params = [self.groupid,address]
        return self.common_request(cmd, params)

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#gettotaltransactioncount
    def getTotalTransactionCount(self):
        cmd = "getTotalTransactionCount"
        params = [self.groupid]
        return self.common_request(cmd, params)


    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getsystemconfigbykey
    def getSystemConfigByKey(self,key):
        cmd = "getSystemConfigByKey"
        params = [self.groupid,key]
        return self.common_request(cmd, params)

    lastblocklimit  = 100;
    lastblocklimittime = 0
    def getBlocklimit(self):
        tick = time.time()
        tickstamp = tick - self.lastblocklimittime
        self.logger.debug("blocklimit tick stamp {}".format(tickstamp))
        if tickstamp < 100: #get blocklimit every 100sec
            return self.lastblocklimit
        for i in range(0,5):#try n times
            try:
                blocknum = self.getBlockNumber()
                oldblocklimit=self.lastblocklimit
                if blocknum > self.lastblocklimit:
                    self.lastblocklimit = blocknum + 500
                    self.logger.info("getBlocklimit:{},blocknum:{},old:{}".format(self.lastblocklimit,blocknum,oldblocklimit))
                    return self.lastblocklimit
            except BcosError as e:
                self.logger.error("getBlocklimit error {}, {}".format(e.code,e.message))
                time.sleep(0.1)

                continue
        return self.lastblocklimit



    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getpendingtransactions
    def call(self,to_address,contract_abi,fn_name,args=None):
        cmd ="call"

        functiondata = encode_transaction_data(fn_name, contract_abi, None, args)
        callmap = dict()
        callmap["data"] = functiondata
        callmap["from"] = self.client_account.address
        callmap["to"] = to_address
        callmap["value"] = 0
        params = [1, callmap]
        # 发送
        response = self.common_request(cmd,params)
        outputdata = response["output"]
        #取得方法的abi，签名，参数 和返回类型，进行call返回值的解析
        fn_abi, fn_selector, fn_arguments = get_function_info(
            fn_name, contract_abi, None, args, None,
        )
        #print("fn_selector",fn_selector)
        #print("fn_arguments",fn_arguments)
        fn_output_types = get_fn_abi_types_single(fn_abi, "outputs")
        #print("output types str:", fn_output_types)
        decoderesult = decode_single(fn_output_types, decode_hex(outputdata))
        return decoderesult

    # https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/api.html#getpendingtransactions
    '''
        可用于所有已知abi的合约，传入abi定义，方法名，正确的参数列表，即可发送交易。交易由BcosClient里加载的账号进行签名。
    '''
    def sendRawTransaction(self,to_address,contract_abi,fn_name,args=None,bin_data=None):
        cmd = "sendRawTransaction"
        # 第三个参数是方法的abi，可以传入None，encode_transaction_data做了修改，支持通过方法+参数在整个abi里找到对应的方法abi来编码
        if(bin_data==None):
            functiondata = encode_transaction_data(fn_name, contract_abi, None, args)
        else:
            functiondata = bin_data
        if(to_address!=None and len(to_address)>0):
            from eth_utils import to_checksum_address
            to_address = to_checksum_address(to_address)
        # 填写一个bcos transaction 的 mapping
        import random
        txmap = dict()
        txmap["randomid"] = random.randint(0, 1000000000)  # 测试用 todo:改为随机数
        txmap["gasPrice"] = 30000000
        txmap["gasLimit"] = 30000000
        txmap["blockLimit"] = self.getBlocklimit()  #501  # 测试用，todo：从链上查一下

        txmap["to"] = to_address
        txmap["value"] = 0
        txmap["data"] = functiondata
        txmap["fiscoChainId"] = self.fiscoChainId
        txmap["groupId"] = self.groupid
        txmap["extraData"] = ""
        # txmap["chainId"]=None #chainId没用了，fiscoChainId有用
        #print(txmap)
        '''
        from datatypes.bcostransactions import (
            serializable_unsigned_transaction_from_dict,
        )
        # 将mapping构建一个transaction对象,非必要，用来对照的
        transaction = serializable_unsigned_transaction_from_dict(txmap)
        # 感受下transaction encode的原始数据
        print(encode_hex(rlp.encode(transaction)))
        '''
        # 实际上只需要用sign_transaction就可以获得rawTransaction的编码数据了,input :txmap,私钥
        signedTxResult = Account.sign_transaction(txmap, self.client_account.privateKey)
        # signedTxResult.rawTransaction是二进制的，要放到rpc接口里要encode下
        params = [self.groupid,encode_hex(signedTxResult.rawTransaction)]
        result = self.common_request(cmd,params)
        return result


    #发送交易后等待共识完成，检索receipt
    def sendRawTransactionGetReceipt(self, to_address, contract_abi, fn_name, args=None, bin_data=None,timeout=15):
        #print("sendRawTransactionGetReceipt",args)
        stat = StatTool.begin()
        txid = self.sendRawTransaction(to_address,contract_abi,fn_name,args,bin_data)
        result = None
        for i in range(0, timeout):
            result = self.getTransactionReceipt(txid)
            #print("getTransactionReceipt : ", result)
            if result == None:
                time.sleep(1)
                self.logger.info("sendRawTransactionGetReceipt,retrying getTransactionReceipt : {}".format(i))
                continue
            else:
                break #get the result break
        stat.done()
        memo = "DONE"
        if result == None:
            memo = "ERROR:TIMEOUT"
        stat.debug("sendRawTransactionGetReceipt,{}".format(memo))
        if result==None:
            raise BcosError(-1, None,"sendRawTransactionGetReceipt,{}".format(memo))
        return result

    '''
        newaddr = result['contractAddress']
        blocknum = result['blockNumber']
    '''
    def deploy(self, contract_bin):
        result = self.sendRawTransactionGetReceipt\
            (to_address="",contract_abi=None,fn_name=None,bin_data=contract_bin)
        newaddr = result['contractAddress']
        blocknum = result['blockNumber']
        #print("onblock : %d newaddr : %s "%(int(blocknum,16),newaddr))
        return result



