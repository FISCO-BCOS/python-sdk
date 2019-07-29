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
  @file: consensus_precompile.py
  @function:
  @author: yujiechen
  @date: 2019-07
'''
from client.common import transaction_common


class ConsensusPrecompile:
    """
    implementation of ConsensusPrecompile
    """

    def __init__(self, contract_path):
        """
        init the address for Consensus contract
        """
        self._consensus_address = "0x0000000000000000000000000000000000001003"
        self.contract_name = "Consensus"
        self.client = transaction_common.TransactionCommon(
            self._consensus_address, contract_path, self.contract_name)

    def __del__(self):
        """
        finish the client
        """
        self.client.finish()

    def addSealer(self, nodeId):
        """
        addSealer
        """
        fn_name = "addSealer"
        fn_args = [nodeId]
        return self.client.send_transaction_getReceipt(fn_name, fn_args)

    def addObserver(self, nodeId):
        """
        addObserver
        """
        fn_name = "addObserver"
        fn_args = [nodeId]
        return self.client.send_transaction_getReceipt(fn_name, fn_args)

    def removeNode(self, nodeId):
        """
        remove Node
        """
        fn_name = "remove"
        fn_args = [nodeId]
        return self.client.send_transaction_getReceipt(fn_name, fn_args)
