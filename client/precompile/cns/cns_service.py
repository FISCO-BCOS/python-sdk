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
  @file: cns_service.py
  @function:
  @author: yujiechen
  @date: 2019-07
'''
import json
import client.clientlogger as clientlogger
from client.common import transaction_common


class CnsService:
    """
    implementation for CNS Service
    """

    def __init__(self, contract_path):
        """
        init the address for CNS contract
        """
        self.logger = clientlogger.logger
        self._cns_address = "0x0000000000000000000000000000000000001004"
        self._max_version_len = 40
        self.define_error_code()
        # define bcosclient
        self.client = transaction_common.TransactionCommon(self._cns_address)
        self.cns_abi_path = contract_path + "/CNS.abi"

    def __del__(self):
        """
        finish the client
        """
        self.client.finish()

    def define_error_code(self):
        """
        common error code for CNS Service
        """
        self._version_exceeds = -51201

    def get_error_msg(self, error_code):
        """
        get error information according to the given error code
        """
        if error_code == self._version_exceeds:
            return "version string length exceeds the maximum limit"

    def register_cns(self, name, version, address, abi):
        """
        register cns contract: (name, version)->address
        precompile api: insert(string,string,string,string)
        """
        # invalid version
        if len(version) > self._max_version_len:
            error_info = self.get_error_msg(self._version_exceeds)
            self.logger.error("register cns failed, error info: {}".format(error_info))
            return error_info

        # call insert function of CNS
        # function definition: insert(string,string,string,string)
        fn_name = "insert"
        fn_args = [name, version, address, json.dumps(abi)]
        return self.client.send_transaction_getReceipt(self.cns_abi_path, fn_name, fn_args)

    def query_cns_by_name(self, name):
        """
        query cns contract information by name
        precompile api: selectByName(string)
        """
        fn_name = "selectByName"
        fn_args = [name]
        return self.client.call_and_decode(self.cns_abi_path, fn_name, fn_args)

    def query_cns_by_nameAndVersion(self, name, version):
        """
        query contract address according to the contract name and version
        precompile api: selectByNameAndVersion(string, string)
        """
        fn_name = "selectByNameAndVersion"
        fn_args = [name, version]
        return self.client.call_and_decode(self.cns_abi_path, fn_name, fn_args)
