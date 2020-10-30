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
import argparse
import sys
import glob
from client.gm_account import GM_Account
from client.stattool import StatTool
from client_config import client_config
from eth_account.account import Account
from eth_utils.hexadecimal import encode_hex
from client.contractnote import ContractNote
from eth_utils.crypto import CRYPTO_TYPE_GM
import json
import os
from client.datatype_parser import DatatypeParser
from eth_utils import to_checksum_address
from console_utils.precompile import Precompile
from console_utils.rpc_console import RPCConsole
from client.common import transaction_common
from client.common import common
from eth_abi.exceptions import InsufficientDataBytes
from console_utils.console_common import *
from client.bcoserror import (
    BcosError,
    CompileError,
    PrecompileError,
    ArgumentsError,
    BcosException,
)
from client.common.transaction_exception import TransactionException
import argcomplete
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
call合约的一个只读接口,解析返回值

>> sendtx [contractname]  [address] [func] [args...]
发送交易调用指定合约的接口，交易如成功，结果会写入区块和状态
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
        gasPrice = 30000000
        # need save address whether or not
        needSaveAddress = True
        args_len = len(inputparams)
        # get the args
        fn_args = inputparams[1:args_len]
        tx_client = transaction_common.TransactionCommon(
            "", contracts_dir, contractname
        )
        result = tx_client.send_transaction_getReceipt(
            None, fn_args, gasPrice, True
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

        pass

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
        if address == "last":
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

        result = tx_client.call_and_decode(fn_name, fn_args)
        print("INFO >> call result:")
        common.print_tx_result(result)

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
        if address == "last":
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
        receipt = tx_client.send_transaction_getReceipt(fn_name, fn_args)[0]
        data_parser = DatatypeParser(default_abi_file(contractname))
        print("\n\nINFO >> from address:  {} ".format(tx_client.keypair.address))
        # 解析receipt里的log 和 相关的tx ,output
        print_receipt_logs_and_txoutput(tx_client, receipt, "", data_parser)
        pass

    def deploylast(self):
        contracts = ContractNote.get_last_contracts()
        for name in contracts:
            print("{} -> {}".format(name, contracts[name]))

    def deploylog(self):
        historys = ContractNote.get_history_list()
        for address in historys:
            print("{} -> {} ".format(address, historys[address]))
