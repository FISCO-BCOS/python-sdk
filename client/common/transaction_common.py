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
from client.bcoserror import BcosError
import client.bcosclient as bcosclient
from client.common.transaction_exception import TransactionException
from client.datatype_parser import DatatypeParser


class TransactionCommon(bcosclient.BcosClient):
    """
    define common functions
    """

    def __init__(self, contract_addr):
        """
        init client to send transactions
        """
        bcosclient.BcosClient.__init__(self)
        self.contract_addr = contract_addr

    @staticmethod
    def get_contract_abi(contract_abi_path):
        """
        get contract abi according to contract_abi_path
        """
        if os.path.exists(contract_abi_path) is False:
            raise Exception("abi file {} not exists".format(contract_abi_path))
        data_parser = DatatypeParser(contract_abi_path)
        contract_abi = data_parser.contract_abi
        return contract_abi

    def send_transaction_getReceipt(self, contract_abi_path, fn_name, fn_args, contract_bin=""):
        """
        send transactions to CNS contract with the givn function name and args
        """
        try:
            contract_abi = TransactionCommon.get_contract_abi(contract_abi_path)
            receipt = super().sendRawTransactionGetReceipt(self.contract_addr,
                                                           contract_abi, fn_name, fn_args)
            # check status
            status = receipt["status"]
            if int(status, 16) != 0:
                raise TransactionException(receipt)
            # check output
            if receipt["output"] is None:
                raise TransactionException(receipt)

        except BcosError as e:
            self.logger.error("send transaction failed, fn_name: {}, fn_args:{}, error_info:{}".
                              format(fn_name, fn_args, e))
            receipt = None
            raise e
        return receipt

    def call_and_decode(self, abi_path, fn_name, fn_args=None):
        """
        call and get the output
        """
        contract_abi = TransactionCommon.get_contract_abi(abi_path)
        result = super().call(self.contract_addr, contract_abi, fn_name, fn_args)
        return result
