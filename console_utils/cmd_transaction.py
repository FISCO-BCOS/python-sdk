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
  @function:
  @author: kentzhang
  @date: 2020-10
'''
import json
import sys


from console_utils.console_common import list_files
from client.common import common
from client.common import transaction_common
from client.contractnote import ContractNote
from client_config import client_config
from console_utils.console_common import fill_params
from client.datatype_parser import DatatypeParser
from console_utils.console_common import default_abi_file
from console_utils.console_common import print_receipt_logs_and_txoutput
import traceback
contracts_dir = "contracts"


class CmdTransaction:
    @staticmethod
    def make_usage():
        usagemsg = []
        usagemsg.append(
            """
>> deploy [contract_name]:
部署合约, 新地址会写入本地记录文件,

>> call [contractname] [address] [func]  [args...]
call合约的一个只读接口,解析返回值,address可以是last或latest,表示调用最近部署的该合约实例

>> sendtx [contractname]  [address] [func] [args...]
发送交易调用指定合约的接口，交易如成功，结果会写入区块和状态，address可以是last或latest,表示调用最近部署的该合约实例
""")
        return usagemsg

    @staticmethod
    def usage():
        usagemsg = CmdTransaction.make_usage()
        for m in usagemsg:
            print(m)

    def deploy(self, inputparams):
        print(inputparams)
        if len(inputparams) == 0:
            sols = list_files(contracts_dir + "/*.sol")
            for sol in sols:
                print(sol + ".sol")
            return
        """deploy abi bin file"""
        # must be at least 2 params
        common.check_param_num(inputparams, 1)
        contractname = inputparams[0].strip()
        # need save address whether or not
        needSaveAddress = True
        args_len = len(inputparams)
        # get the args
        fn_args = inputparams[1:args_len]

        tx_client = transaction_common.TransactionCommon(
            "", contracts_dir, contractname
        )

        try:
            result = tx_client.send_transaction_getReceipt(
                None, fn_args, deploy=True
            )[0]
            print("INFO >> client info: {}".format(tx_client.getinfo()))
            print(
                "deploy result  for [{}] is:\n {}".format(
                    contractname, json.dumps(result, indent=4)
                )
            )
            name = contractname
            address = result["contractAddress"]
            blocknum = int(result["blockNumber"], 16)
            txhash = result["transactionHash"]
            ContractNote.save_contract_address(name, address)
            print("on block : {},address: {} ".format(blocknum, address))
            if needSaveAddress is True:
                ContractNote.save_address_to_contract_note(name, address)
                print("address save to file: ", client_config.contract_info_file)
            else:
                print(
                    """\nNOTE : if want to save new address as last
                    address for (call/sendtx)\nadd 'save' to cmdline and run again"""
                )
            ContractNote.save_history(name, address, blocknum, txhash)
        except Exception as e:
            print("deploy exception! ", e)
            traceback.print_exc()
            tx_client.finish()

    def call(self, inputparams):
        if len(inputparams) == 0:
            sols = list_files(contracts_dir + "/*.sol")
            for sol in sols:
                print(sol + ".sol")
            return
        common.check_param_num(inputparams, 3)
        paramsname = ["contractname", "address", "func"]
        params = fill_params(inputparams, paramsname)
        contractname = params["contractname"]
        address = params["address"]
        if address == "last" or address == "latest":
            address = ContractNote.get_last(contractname)
            if address is None:
                sys.exit(
                    "can not get last address for [{}],break;".format(contractname)
                )

        tx_client = transaction_common.TransactionCommon(
            address, contracts_dir, contractname
        )
        fn_name = params["func"]
        fn_args = inputparams[3:]
        print("INFO>> client info: {}".format(tx_client.getinfo()))
        print(
            "INFO >> call {} , address: {}, func: {}, args:{}".format(
                contractname, address, fn_name, fn_args
            )
        )
        try:
            result = tx_client.call_and_decode(fn_name, fn_args)
            print("INFO >> send from {}, result:".format(tx_client.keypair.address))
            common.print_tx_result(result)

        except Exception as e:
            traceback.print_exc()
            print("call exception! ", e)
            tx_client.finish()

    # 2021.02版本已经支持创建不同的账户来发送交易，考虑到python命令行控制台的输入繁琐（也不像java控制台这样是预加载账户
    # 所以暂时未支持在控制台命令行传入账户名，如需用不同账户发送交易，可以切换到不同的目录或配置文件
    # 如果自己写代码调用，则可以指定不同的账户了
    def sendtx(self, inputparams):
        if len(inputparams) == 0:
            sols = list_files(contracts_dir + "/*.sol")
            for sol in sols:
                print(sol + ".sol")
            return
        common.check_param_num(inputparams, 3)
        paramsname = ["contractname", "address", "func"]
        params = fill_params(inputparams, paramsname)
        contractname = params["contractname"]
        address = params["address"]
        if address == "last" or address == "latest":
            address = ContractNote.get_last(contractname)
            if address is None:
                sys.exit(
                    "can not get last address for [{}],break;".format(contractname)
                )

        tx_client = transaction_common.TransactionCommon(
            address, contracts_dir, contractname
        )
        fn_name = params["func"]
        fn_args = inputparams[3:]
        print("INFO>> client info: {}".format(tx_client.getinfo()))
        print(
            "INFO >> sendtx {} , address: {}, func: {}, args:{}".format(
                contractname, address, fn_name, fn_args
            )
        )
        try:
            account = None
            # from client.bcosclient import BcosClient
            # (account,keypair) = BcosClient.load_ecdsa_account("bin/accounts/tester.keystore","123456")
            # print(keypair.address)
            # 不指定from账户，如需指定，参考上面的加载，或者创建一个新的account，
            # 参见国密（client.GM_Account）和非国密的account管理类LocalAccount
            (receipt, output) = tx_client.send_transaction_getReceipt(
                fn_name, fn_args, from_account=account)
            data_parser = DatatypeParser(default_abi_file(contractname))
            # 解析receipt里的log 和 相关的tx ,output
            print_receipt_logs_and_txoutput(tx_client, receipt, "", data_parser)
        except Exception as e:
            print("send tx exception! ", e)
            traceback.print_exc()
            tx_client.finish()

    def deploylast(self):
        contracts = ContractNote.get_last_contracts()
        for name in contracts:
            print("{} -> {}".format(name, contracts[name]))

    def deploylog(self):
        historys = ContractNote.get_history_list()
        for address in historys:
            print("{} -> {} ".format(address, historys[address]))
