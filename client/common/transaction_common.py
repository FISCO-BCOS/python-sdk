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
  @file: transaction_common.py
  @function:
  @author: yujiechen
  @date: 2019-07
'''
import os
from client.common import common
from client.datatype_parser import DatatypeParser
from client.common.compiler import Compiler
import client.bcosclient as bcosclient
from eth_utils import to_checksum_address
from client.bcoserror import BcosError, CompileError, ArgumentsError
from client.common.transaction_exception import TransactionException


class TransactionCommon(bcosclient.BcosClient):
    """
    define common functions
    """

    def __init__(self, contract_addr, contract_path, contract_name):
        """
        init client to send transactions
        """
        bcosclient.BcosClient.__init__(self)
        self.contract_addr = contract_addr
        self.contract_path = contract_path
        self.contract_abi_path = contract_path + "/" + contract_name + ".abi"
        self.contract_bin_path = contract_path + "/" + contract_name + ".bin"
        self.sol_path = contract_path + "/" + contract_name + ".sol"

    def __del__(self):
        super().finish()

    def gen_contract_abi(self, needCover=False):
        """
        get contract abi according to contract_abi_path
        """
        if needCover is False and os.path.exists(self.contract_abi_path) is True:
            return
        # backup the abi and bin
        else:
            force_write = common.backup_file(self.contract_abi_path)
            if force_write is False:
                return
            force_write = common.backup_file(self.contract_bin_path)
            if force_write is False:
                return
        Compiler.compile_file(self.sol_path, self.contract_path)

    def send_transaction_getReceipt(self, fn_name, fn_args, deploy=False):
        """
        send transactions to CNS contract with the givn function name and args
        """
        try:
            contract_abi, args = self.format_args(fn_name, fn_args, deploy)
            contract_bin = None
            if deploy is True and os.path.exists(self.contract_bin_path) is True:
                with open(self.contract_bin_path) as f:
                    contract_bin = f.read()
            receipt = super().sendRawTransactionGetReceipt(self.contract_addr,
                                                           contract_abi, fn_name,
                                                           args, contract_bin)
            # check status
            status = receipt["status"]
            if int(status, 16) != 0:
                raise TransactionException(receipt)
            # check output
            if receipt["output"] is None:
                raise TransactionException(receipt)
            return receipt
        except BcosError as e:
            self.logger.error("send transaction failed, fn_name: {}, fn_args:{}, error_info:{}".
                              format(fn_name, fn_args, e))
            receipt = None
            raise e
        except CompileError as e:
            self.logger.error(("send transaction failed for compile soldity failed,"
                               "contract_path {}, error_info:{}").
                              format(self.sol_path, e))

    @staticmethod
    def format_args_by_abi(inputparams, inputabi):
        paramformatted = []
        index = -1
        if len(inputparams) != len(inputabi):
            raise ArgumentsError(("Invalid Arguments {}, expected params size: {},"
                                  " inputted params size: {}".format(inputparams,
                                                                     len(inputabi),
                                                                     len(inputparams))))
        for input_item in inputabi:
            index += 1
            param = inputparams[index]
            if '\'' in param:
                param = param.replace('\'', "")
            if "int" in input_item["type"]:
                paramformatted.append(int(param, 10))
                continue
            if "address" in input_item["type"]:
                print("to checksum address ", param)
                try:
                    paramformatted.append(to_checksum_address(param))
                except ArgumentsError as e:
                    raise ArgumentsError(("ERROR >> covert {} to to_checksum_address failed,"
                                          " exception: {}").format(param, e))
                continue
            paramformatted.append(param)
        print("INFO >> param formatted by abi:", paramformatted)
        return paramformatted

    def format_args(self, fn_name, fn_args, needCover=False):
        """
        format args
        """
        self.gen_contract_abi()
        data_parser = DatatypeParser(self.contract_abi_path)
        contract_abi = data_parser.contract_abi
        if fn_args is None:
            return (contract_abi, fn_args)
        inputabi = data_parser.func_abi_map_by_name[fn_name]["inputs"]
        args = TransactionCommon.format_args_by_abi(fn_args, inputabi)
        return (contract_abi, args)

    def call_and_decode(self, fn_name, fn_args=None):
        """
        call and get the output
        """
        contract_abi, args = self.format_args(fn_name, fn_args, False)
        result = super().call(self.contract_addr, contract_abi, fn_name, args)
        return result
