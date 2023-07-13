#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
  FISCO BCOS/Python-SDK is a python client for FISCO BCOS3.0 (https://github.com/FISCO-BCOS/)
  FISCO BCOS/Python-SDK is free software: you can redistribute it and/or modify it under the
  terms of the MIT License as published by the Free Software Foundation. This project is
  distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Thanks for
  authors and contributors of eth-abi, eth-account, eth-hash，eth-keys, eth-typing, eth-utils,
  rlp, eth-rlp , hexbytes ... and relative projects
  @author: kentzhang
  @date: 2022-09
  # reference :https://fisco-bcos-doc.readthedocs.io/zh_CN/latest/docs/develop/api.html
  useful helper:
  int(num,16)  hex -> int
  hex(num)  : int -> hex
'''
import itertools
import json
import sys
import time
from ctypes import byref, c_char_p, POINTER, c_void_p, c_int

from bcos3sdk.bcos3callbackfuture import BcosCallbackFuture
from bcos3sdk.bcos3datadef import *
from bcos3sdk.bcos3sdkconfig import Bcos3SDKConfig
from client.datatype_parser import DatatypeParser
from client_config import client_config
from bcos3sdk.bcos3sdk_wrap import NativeBcos3sdk,  \
    BCOS_AMOP_SUB_CALLBACK_FUNC,  BCOS_AMOP_PUBLISH_CALLBACK_FUNC
from client import clientlogger
from client.bcoserror import BcosException
from client.common import common
from client.common import transaction_status_code
from client.signer_impl import Signer_GM, Signer_ECDSA, Signer_Impl
from eth_abi import decode_abi
from eth_utils.crypto import CRYPTO_TYPE_GM, CRYPTO_TYPE_ECDSA, set_crypto_type
from eth_utils.hexadecimal import decode_hex, encode_hex
from utils.abi import get_abi_output_types
from utils.contracts import encode_transaction_data
from utils.contracts import get_aligned_function_data
from utils.contracts import get_function_info


class Bcos3Client:
    name = "bcos3"
    default_from_account_signer: Signer_Impl = None
    chainid = ""
    group = ""
    node = None
    keypair = None
    bcos3sdk = None
    logger = clientlogger.logger  # logging.getLogger("BcosClient")
    config = None
    sdk_version = None
    request_counter = itertools.count()
    
    def __init__(self, client_config_instance=client_config):
        self.lastblocklimittime = 0
        self.init(client_config_instance)
    
    def __del__(self):
        """
        release the resources
        """
        self.finish()

    
    def init(self,client_config_instance=client_config):
        self.config = client_config_instance ;
        self.crypto_enum = 0  # 0 for ECDSA 1 for GM
        if self.config.crypto_type.upper() == "GM":
            self.crypto_enum = 1
        set_crypto_type(self.config.crypto_type)  # 使其全局生效
        self.blockLimit = 500
        self.group = self.config.bcos3_group
        self.init_clib_sdk()
        self.bcos3sdkconfig = Bcos3SDKConfig(self.config.bcos3_config_file)
        if client_config.bcos3_check_node_version :
            try:
                self.check_node_version()
            except Exception as e:
                if client_config.bcos3_when_version_mismatch == "WARN":
                    print(f"!!! [WARN] CHECK NODE VERSION EXCEPTION(But still continue): {e}  \n")
                else:
                    raise  e
            
        return self
    

    def check_node_version(self):
        majorVersion = client_config.bcos3_major_version
        maxMinorVersion = client_config.bcos3_max_miner_version
        groupInfo = self.getGroupInfo()
        strInfo = ""
        version = ""
        # cyber 202303 by kent
        for node in groupInfo["nodeList"]:
            try:
                strInfo = node["iniConfig"]
                nodeInfo = json.loads(strInfo)
                version = nodeInfo["binaryInfo"]["version"]
                major, minor, patch = version.split(".")
                if int(major) == majorVersion and int(minor) <= maxMinorVersion:
                    return True
                else:
                    raise Exception(f"Python-sdk is NOT Fully Verified for node version [{version}] yet")
            except KeyError as e:
                raise Exception(f"Check node version,Missing field in JSON :{e}. {strInfo}")
            except ValueError as e:
                raise Exception(f"Check node version,Invalid version format : {version}",e)
        return True
        
    
    def init_clib_sdk(self):
        self.seq = 0
        self.bcossdk = NativeBcos3sdk()
        self.load_default_account()
        # print("init_sdk: {self.config.bcos3lib_config_file}")
        res = self.bcossdk.init_sdk(self.config.bcos3_config_file, self.config.bcos3_lib_path)
        if res != 0:
            msg = self.bcossdk.bcos_sdk_get_last_error_msg()
            raise BcosException(f"START SDK error res:{res},[{msg}]")
        privkey = self.default_from_account_signer.get_keypair().private_key
        if type(privkey) is str:
            privkey = decode_hex(privkey)
        #print("privatekey:",privkey)
        self.keypair = self.bcossdk.bcos_sdk_create_keypair_by_private_key(self.crypto_enum, privkey, len(privkey))
        chainid = self.bcossdk.bcos_sdk_get_group_chain_id(self.bcossdk.sdk, s2b(self.group))
        self.chainid = ctypes.string_at(chainid)
        self.bcossdk.bcos_sdk_c_free(chainid)
        return 0
    
    def get_last_errormsg(self):
        res = self.bcossdk.bcos_sdk_get_last_error_msg()
        return b2s(res)
    
    
    def get_last_error(self):
        res= self.bcossdk.bcos_sdk_get_last_error()
        return res

    def get_last_error_full(self):
        ret = self.get_last_error()
        msg = self.get_last_errormsg()
        return (ret,msg)
    
    # load the account from keyfile
    def load_default_account(self):
        if self.default_from_account_signer is not None:
            return  # 不需要重复加载
        # 默认的 ecdsa 账号
        
        if self.config.crypto_type == CRYPTO_TYPE_ECDSA:
            self.account_file = "{}/{}".format(self.config.account_keyfile_path,
                                               self.config.account_keyfile)
            
            self.default_from_account_signer = Signer_ECDSA.from_key_file(
                self.account_file, self.config.account_password)
            
        # 加载默认国密账号
        if self.config.crypto_type == CRYPTO_TYPE_GM:
            self.account_file = "{}/{}".format(self.config.account_keyfile_path,
                                               self.config.gm_account_keyfile)
            self.default_from_account_signer = Signer_GM.from_key_file(
                self.account_file, self.config.account_password)

    
    def finish(self):
        # print("do finish")
        if self.keypair is not None:
            self.bcossdk.bcos_sdk_destroy_keypair(self.keypair)
            self.keypair = None
        self.bcossdk.finish()

    # 返回能完整标识此客户端的字符串，先简单点，可以根据场景扩展，比如增加ip地址端口等
    def get_full_name(self):
        #id 由 chainid 和group组成，对应一个账本，以便区分部署的合约地址
        fullname = f"{self.name}-{b2s(self.chainid)}-{b2s(self.group)}"
        return fullname
    
    def getinfo(self):
        info = ""
        info += "chain:[{}];".format(b2s(self.chainid))
        info += "group:[{}];".format(self.group)
        info += "crypto: [{}];".format(self.config.crypto_type)
        address = self.bcossdk.bcos_sdk_get_keypair_address(self.keypair)
        info += f"account:[{b2s(ctypes.string_at(address))}];"
        self.bcossdk.bcos_sdk_c_free(address)
        info += f"peers:[{self.bcos3sdkconfig.peers}];"
        if self.sdk_version is None:
            self.sdk_version = b2s(self.bcossdk.bcos_sdk_version())
        info = f"{info}\nNative SDK Version : {self.sdk_version}"
        return info
    
    def wait_result(self, future: BcosCallbackFuture):
        (is_timeout, response) = future.wait()
        if is_timeout:
            raise BcosException(f"bcos sdk timeout {future.context.msg}")
        # print(f"response context(callback): {future.context_callback.detail()}")
        return self.get_result(response.data)
    
    def get_result(self, response_data):
        # print(f"data is {response_data}")
        if response_data is None or len(response_data) == 0:
            raise BcosException(f"Response error: {[response_data]}")
        try:
            #处理可能不是json的情况
            response = json.loads(response_data)
        except Exception as e:
            return response_data
        if "error" in response:
            raise BcosException(response_data)
        if "result" not in response:
            raise BcosException(response_data)

        # print(f"response :{response}")
        result = response["result"]
        if type(result) is str:
            try:
                result = json.loads(result)  # 有几个接口被转成了str返回，实际上是json对象
            except Exception as e:
                # 有的result里直接就是str值，无需转json，比如getBlockHashByNumber
                pass
        return result
    
    def getBlockNumber(self):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, f"{sys._getframe().f_code.co_name}")
        self.bcossdk.bcos_rpc_get_block_number(self.bcossdk.sdk, s2b(self.group), s2b(self.node), cbfuture.callback,
                                               byref(cbfuture.context))
        
        result = self.wait_result(cbfuture)
        num = result
        return num
    
    def getPbftView(self):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_pbft_view(self.bcossdk.sdk, s2b(self.group), s2b(self.node), cbfuture.callback,
                                            byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getSealerList(self):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_sealer_list(self.bcossdk.sdk, s2b(self.group), s2b(self.node), cbfuture.callback,
                                              byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getObserverList(self):
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_observer_list(self.bcossdk.sdk, s2b(self.group), s2b(self.node), cbfuture.callback,
                                                byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getConsensusStatus(self):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_consensus_status(self.bcossdk.sdk, s2b(self.group), s2b(self.node), cbfuture.callback,
                                                   byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getSyncStatus(self):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_sync_status(self.bcossdk.sdk, s2b(self.group), s2b(self.node), cbfuture.callback,
                                              byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getPeers(self):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_peers(self.bcossdk.sdk, cbfuture.callback, byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getGroupInfo(self):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_group_info(self.bcossdk.sdk,s2b(self.group),cbfuture.callback,
                                              byref(cbfuture.context));
        return self.wait_result(cbfuture)
    
    def getGroupPeers(self):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_group_peers(self.bcossdk.sdk, s2b(self.group), cbfuture.callback,
                                              byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getGroupList(self):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_group_list(self.bcossdk.sdk, cbfuture.callback, byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getBlockByHash(self, block_hash, only_header=0, only_tx_hash=0):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_block_by_hash(self.bcossdk.sdk, s2b(self.group), s2b(self.node),
                                                s2b(block_hash),
                                                only_header,
                                                only_tx_hash,
                                                cbfuture.callback, byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getBlockByNumber(self, num, only_header=0, only_tx_hash=0):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_block_by_number(self.bcossdk.sdk, s2b(self.group), s2b(self.node),
                                                  num,
                                                  only_header,
                                                  only_tx_hash,
                                                  cbfuture.callback, byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getBlockHashByNumber(self, num):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_block_hash_by_number(self.bcossdk.sdk, s2b(self.group), s2b(self.node),
                                                       num,
                                                       cbfuture.callback, byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getTransactionByHash(self, hash, proof=0):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_transaction(self.bcossdk.sdk, s2b(self.group), s2b(self.node),
                                              s2b(hash),
                                              proof,
                                              cbfuture.callback, byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getTransactionReceipt(self, hash, proof=0):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_transaction_receipt(self.bcossdk.sdk, s2b(self.group), s2b(self.node),
                                                      s2b(hash),
                                                      proof,
                                                      cbfuture.callback, byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getPendingTxSize(self):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_pending_tx_size(self.bcossdk.sdk, s2b(self.group), s2b(self.node),
                                                  cbfuture.callback, byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getCode(self, address):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_code(self.bcossdk.sdk, s2b(self.group), s2b(self.node),
                                       s2b(address),
                                       cbfuture.callback, byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getTotalTransactionCount(self):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_total_transaction_count(self.bcossdk.sdk, s2b(self.group), s2b(self.node),
                                                          cbfuture.callback, byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getSystemConfigByKey(self, key):
        next(self.request_counter)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_get_system_config_by_key(self.bcossdk.sdk, s2b(self.group), s2b(self.node),
                                                       s2b(key),
                                                       cbfuture.callback, byref(cbfuture.context))
        return self.wait_result(cbfuture)
    
    def getBlocklimit(self):
        
        tick = time.time()
        tickstamp = tick - self.lastblocklimittime
        if tickstamp < 30 and self.blockLimit > 500:  # get blocklimit every 30sec
            return self.blockLimit
        next(self.request_counter)
        new_blockLimit = self.bcossdk.bcos_rpc_get_block_limit(self.bcossdk.sdk, s2b(self.group))
        if new_blockLimit >= self.blockLimit:
            self.blockLimit = new_blockLimit
        self.lastblocklimittime = time.time()
        return self.blockLimit
    
    def call(self, to_address, contract_abi, fn_name,args=None,raw_func_data=None):
        next(self.request_counter)
        cmd = "call"
        if to_address != "":
            common.check_and_format_address(to_address)
        
        self.load_default_account()
        if raw_func_data is None:
            functiondata = encode_transaction_data(fn_name, contract_abi, None, args)
        else:
            functiondata = raw_func_data
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        self.bcossdk.bcos_rpc_call(self.bcossdk.sdk, s2b(self.group), s2b(self.node), s2b(to_address),
                                   s2b(functiondata),
                                   cbfuture.callback, byref(cbfuture.context))
        response = self.wait_result(cbfuture)
        # print(f"in call response is {response},cbfuture context {cbfuture.context.detail()}")
        if "status" in response.keys():
            status = response["status"]
            error_message = transaction_status_code.TransactionStatusCode.get_error_message(status)
            if error_message is not None:
                raise BcosException(
                    "call error, status:{},error message: {}".format(status, error_message))

        if "output" in response.keys() and contract_abi is not None and fn_name is not None:
            outputdata = response["output"]
            # 取得方法的abi，签名，参数 和返回类型，进行call返回值的解析
            fn_abi, fn_selector, fn_arguments = get_function_info(
                fn_name, contract_abi, None, args, None,
            )
            
            fn_output_types = get_abi_output_types(fn_abi)
            try:
                outputresult = decode_abi(fn_output_types, decode_hex(outputdata))
                return outputresult
            except BaseException as e:
                return response
        


        return response
    
    '''
        可用于所有已知abi的合约，传入abi定义，方法名，正确的参数列表，即可发送交易。交易由BcosClient里加载的账号进行签名。
    '''
    def sendRawTransactionData(self,  raw_tx_data):
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        
        self.bcossdk.bcos_rpc_send_transaction(self.bcossdk.sdk, s2b(self.group), s2b(self.node),
                                               s2b(raw_tx_data),
                                               0, cbfuture.callback, byref(cbfuture.context))
        result = self.wait_result(cbfuture)
        return result
    
    def sendRawTransaction(self, to_address, contract_abi, fn_name, args=None,
                           function_bin_data=None, raw_tx_data=None,extra_abi=None):
        next(self.request_counter)
        if to_address is None:
            to_address = ""
        if to_address != "":
            common.check_and_format_address(to_address)
        # 第三个参数是方法的abi，可以传入None，encode_transaction_data做了修改，支持通过方法+参数在整个abi里找到对应的方法abi来编码
        if function_bin_data is None:
            functiondata = encode_transaction_data(fn_name, contract_abi, None, args)
        # the args is None
        elif args is None:
            functiondata = function_bin_data
        else:
            # deploy with params,need contract_abi and args
            fn_data = get_aligned_function_data(contract_abi, None, args)
            functiondata = function_bin_data + fn_data[2:]
        blocklimit =self.getBlocklimit()
        # ------------------------------
        # 这一段是验证多个api组合实现交易签名的，等效于bcos_sdk_create_signed_transaction,这一段仅留作示例
        #txdataObj 实际上对应的是(bcostars::TransactionData*)这个结构体的指针，不是一段数据，是不能打印和算hash的
        # 在cpp sdk里TransactionBuilder::createTransactionData时，会使用genRandomUint256生成nonce
        # 所以每次调用bcos_sdk_create_transaction_data的数据都是不一样的，txdatahash也是不一样的
        #------------------------------------
        # txdataObj = self.bcossdk.bcos_sdk_create_transaction_data(s2b(self.group), s2b(self.chainid),s2b(to_address), s2b(functiondata), s2b(extra_abi),
        #                                                           blocklimit )
        # txdatahash_p  =self.bcossdk.bcos_sdk_calc_transaction_data_hash(0, txdataObj) #要free它
        # txdatahash =  ctypes.string_at(txdatahash_p)
        # signres = self.bcossdk.bcos_sdk_sign_transaction_data_hash(self.keypair,txdatahash)
        # signedtx_p = self.bcossdk.bcos_sdk_create_signed_transaction_with_signed_data(txdataObj,signres,txdatahash,0) #要free它
        # print(ctypes.string_at(signedtx) )
        # 最后要调用 bcos_sdk_destroy_transaction_data
        #------------------------------------------
       
        # if to_address is not None and len(to_address) > 0:
        #    from eth_utils import to_checksum_address
        #    to_address = to_checksum_address(to_address)
        p_txhash = c_char_p(0)
        p_signed_tx = c_char_p(0)
        self.bcossdk.bcos_sdk_create_signed_transaction(self.keypair, s2b(self.group), s2b(self.chainid),
                                                        s2b(to_address), s2b(functiondata), s2b(extra_abi),
                                                        blocklimit, 0,
                                                        p_txhash, p_signed_tx)

        result = self.sendRawTransactionData(p_signed_tx.value);
        #must free buffer alloc by bcos_sdk_create_signed_transaction * todo:check memory leak (?)
        self.bcossdk.bcos_sdk_c_free(p_signed_tx)
        self.bcossdk.bcos_sdk_c_free(p_txhash)
        
        return result
    
    def deploy(self, contractbin, contract_abi=None, fn_args=None):
        return self.sendRawTransaction(to_address="",
                                       function_bin_data=contractbin,
                                       contract_abi=contract_abi,
                                       fn_name=None,
                                       args=None,
                                       extra_abi=contract_abi)
    
    def deployFromFile(
            self,
            contractbinfile,
            contract_abi=None,
            fn_args=None):

        with open(contractbinfile, "rb") as f:
            contractbin = f.read()
            f.close()
        if contractbinfile.endswith("wasm"):
            #wasm文件存的是二进制，所以读的时候要rb，读出来后要encode
            contractbin = encode_hex(contractbin)
        else:
            contractbin = bytes.decode(contractbin, "utf-8")
            
        result = self.deploy(contractbin, contract_abi, fn_args)
        return result


    def event_subscribe(self,address,event_name="",contract_abi="",topics=[],fromBlock=-1,toBlock=-1):
        event_param = dict()
        event_param["fromBlock"] = fromBlock # -1 表示最新
        event_param["toBlock"] = toBlock  # -1表示最新
        event_param["address"] = [address]  # sample helloWorld address
        if topics is not None and len(topics)>0:
            event_param["topics"] = topics
        else:
            #根据event_name获取topics，一般采用这种方法
            parser = DatatypeParser()
            parser.set_abi(contract_abi)
            eventtopic = parser.topic_from_event_name(event_name)
            event_param["topics"]=[eventtopic]

        event_param_json = json.dumps(event_param)
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        subid = self.bcossdk.bcos_event_sub_subscribe_event(self.bcossdk.sdk, s2b(self.group), s2b(event_param_json), cbfuture.callback,
                                                   byref(cbfuture.context))
        return (subid,cbfuture)
    
    def event_unsubscribe(self,subid):
        self.bcossdk.bcos_event_sub_unsubscribe_event(subid)


    def amop_subscribe(self,topiclist):
        ctopiclist = strarr2ctypes(topiclist)
        self.bcossdk.bcos_amop_subscribe_topic(self.bcossdk.sdk, ctopiclist, len(ctopiclist))
        
    def amop_set_subscribe_topic_cb(self,cbfunc,context_):
        context = 0
        if context_ is not None and context_ != 0:
            context =byref(context_)
        self.bcossdk.bcos_amop_set_subscribe_topic_cb(self.bcossdk.sdk,(BCOS_AMOP_SUB_CALLBACK_FUNC)(cbfunc),
                                         context)
        
        
    callback = None
    def amop_subscribe_with_cb(self,topic):
    
        cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")

        #self.callback = BCOS_AMOP_SUB_CALLBACK_FUNC(cbfuture.amop_callback)
        self.bcossdk.bcos_amop_subscribe_topic_with_cb(self.bcossdk.sdk,s2b(topic),
                                                       cbfuture.amop_callback,
                                                       byref(cbfuture.context))
        return cbfuture
    
    def amop_publish(self,topic,data,future=None,timeout_=10000):
        if future ==None:
            future = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
        cbfunc =future.amop_publish_callback
        #print("publish callback: ",cbfunc)
        self.bcossdk.bcos_amop_publish(self.bcossdk.sdk, s2b(topic),
                                       (s2b(data)), len(data),
                                       (c_int)(timeout_),
                                       cbfunc,
                                       byref(future.context)
                                       )
        return future
    
    def amop_broadcast(self,topic,data=None):
        self.bcossdk.bcos_amop_broadcast(self.bcossdk.sdk,s2b(topic),s2b(data),len(data))
        
    def amop_send_response(self,peer,seq,data):
        self.bcossdk.bcos_amop_send_response(self.bcossdk.sdk,s2b(peer),s2b(seq),s2b(data),len(data))
        
