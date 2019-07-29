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
  @file: precompile.py
  @function:
  @author: yujiechen
  @date: 2019-07
'''
import os
import json
from eth_utils import to_checksum_address
from client.bcoserror import PrecompileError
from client.bcoserror import ArgumentsError
from client.common.transaction_exception import TransactionException
from client.precompile.cns.cns_service import CnsService
from client.precompile.consensus.consensus_precompile import ConsensusPrecompile
from client.precompile.config.config_precompile import ConfigPrecompile
from client.precompile.permission.permission_service import PermissionService


class Precompile:
    """
    """
    functions = {}
    def __init__(self, cmd, args, contract_path):
        self._cmd = cmd
        self._args = args
        self._contract_path = contract_path
        Precompile.define_functions()

    @staticmethod
    def define_functions():
        """
        define all cmds
        """
        # cns
        Precompile.functions["cns"] = ["registerCNS", "queryCNSByName", "queryCNSByNameAndVersion"]
        # consensus
        Precompile.functions["consensus"] = ["addSealer", "addObserver", "removeNode"]
        # configuration system contract
        Precompile.functions["sysconfig"] = ["setSystemConfigByKey"]
        # permission precompile
        Precompile.functions["permission"] = ["grantUserTableManager", "grantPermissionManager",
                                        "grantNodeManager", "grantCNSManager",
                                        "grantSysConfigManager", "revokeUserTableManager",
                                        "revokeDeployAndCreateManager", "revokePermissionManager",
                                        "revokeNodeManager", "revokeCNSManager",
                                        "revokeSysConfigManager", "listUserTableManager",
                                        "listDeployAndCreateManager",
                                        "listPermissionManager", "listNodeManager",
                                        "listSysConfigManager"]

    def print_cns_usage(self, print_all=False):
        """
        print cns usage
        """
        prefix = "CNS USAGE NOTE:"
        if print_all:
            print("INFO >> CNS Usage:")
            prefix = "\t"
        if print_all is True or self._cmd == self.functions["cns"][0]:
            print(("{} {} [contract_name] [contract_address]"
                  " [contract_version]").format(prefix, self.functions["cns"][0]))
        if print_all is True or self._cmd == self.functions["cns"][1]:
            print("{} {} [contract_name]".
                  format(prefix, self.functions["cns"][1]))
        if print_all is True or self._cmd == self.functions["cns"][2]:
            print('''{} {} [contract_name] [contract_version]'''.
                  format(prefix, self.functions["cns"][2]))

    def print_consensus_usage(self, print_all=False):
        """
        print usage information for consensus precompile
        """
        prefix = "CONSENSUS USAGE NOTE:"
        if print_all:
            print("INFO >> CONSENSUS Usage:")
            prefix = "\t"
        if print_all is True or self._cmd == self.functions["consensus"][0]:
            print('''{} {} [nodeId]'''.format(prefix, self.functions["consensus"][0]))
        if print_all is True or self._cmd == self.functions["consensus"][1]:
            print('''{} {} [nodeId]'''.format(prefix, self.functions["consensus"][1]))
        if print_all is True or self._cmd == self.functions["consensus"][2]:
            print('''{} {} [nodeId]'''.format(prefix, self.functions["consensus"][2]))

    def print_sysconfig_usage(self, print_all=False):
        """
        print usage for sysconfig precompile
        """
        prefix = "SYSCONFIG USAGE NOTE: "
        if print_all:
            print("INFO >> SYSCONFIG Usage:")
            prefix = "\t"
        if print_all is True or self._cmd == self.functions["sysconfig"][0]:
            print('''{} {} [key(tx_count_limit/tx_gas_limit)] [value]'''.
                  format(prefix, self.functions["sysconfig"][0]))

    def print_permission_usage(self):
        """
        print usage information for permission
        """
        if self._cmd.startswith("grantUserTable") or self._cmd.startswith("revokeUserTable"):
            print('''USAGE NOTE:  {} [tableName] [account_adddress]'''.
                  format(self._cmd))
        else:
            print('''USAGE NOTE:  {} [account_adddress]'''.format(self._cmd))

    @staticmethod
    def print_all_permission_usage():
        """
        print all permission usage
        """
        print("INFO >> Permission Usage:")
        for cmd in Precompile.functions["permission"]:
            if cmd.startswith("grantUserTable") or cmd.startswith("revokeUserTable"):
                print('''\t{} [tableName] [account_adddress]'''.
                  format(cmd))
            else:
                print('''\t{} [account_adddress]'''.format(cmd))
    
    @staticmethod
    def get_all_cmd():
        """
        get all cmd
        """
        cmds = []
        for cmd_array in Precompile.functions:
            for cmd in Precompile.functions[cmd_array]:
                cmds.append(cmd)
        return cmds

    def print_error_msg(self, err_msg):
        """
        print error msg
        """
        print("ERROR >> call {} failed for {}".format(self._cmd, err_msg))

    def print_transaction_exception(self, transaction_exception):
        error_msg = '''send transaction failed\n, >> INFO\n {},
                    {}'''.format(transaction_exception.get_status_error_info(),
                                 transaction_exception.get_output_error_info())
        self.print_error_msg(error_msg)

    def print_succ_msg(self, msg=None):
        """
        print succ msg
        """
        if msg is None:
            print("INFO >> {} Succ".format(self._cmd))
        else:
            print("INFO >> {} Succ, result msg:\n>>INFO {}".format(self._cmd, msg))

    def check_abi(self, abi_path):
        """
        check abi path
        """
        if os.path.exists(abi_path) is False:
            self.print_error_msg("abi file {} not exists".format(abi_path))
            return False
        return True

    def check_and_format_address(self, address):
        """
        check and format address
        """
        try:
            formatted_address = to_checksum_address(address)
            return formatted_address
        except Exception as e:
            self.print_error_msg(
                "covert {} to checksum_address failed, error info {}".format(address, e))
            return None

    def check_param_num(self, expected):
        """
        check param num
        """
        if len(self._args) < expected:
            raise ArgumentsError(
                '''invalid arguments, expected num: {},
                real num: {}'''.format(expected, len(self._args)))

    @staticmethod
    def print_cns_info(cns_info):
        """
        print cns information
        """
        for cns_item in cns_info:
            cns_obj = json.loads(cns_item)
            i = 0
            for cns in cns_obj:
                print("CNS ITEM {} >>".format(i))
                print("\tContractName: {}".format(cns["name"]))
                print("\tContractVersion: {}".format(cns["version"]))
                print("\tContractAddress: {}".format(cns["address"]))
                i = i + 1

    def call_cns(self):
        """
        call cns service
        register name, version, address, abi
        queryCNSByName name
        queryCnsByNameAndVersion name version
        """
        if self._cmd not in self.functions["cns"]:
            return
        self.cns_service = CnsService(self._contract_path)
        try:
            # register cns contract
            if self._cmd == self.functions["cns"][0]:
                self.check_param_num(3)
                contract_name = self._args[0]
                contract_version = self._args[2]
                # check address
                contract_address = self.check_and_format_address(self._args[1])
                if contract_address is None:
                    return
                try:
                    self.cns_service.register_cns(
                        contract_name, contract_version, contract_address, "")
                    self.print_succ_msg()
                except TransactionException as e:
                    self.print_transaction_exception(e)
                return
            # query cns information by name
            if self._cmd == self.functions["cns"][1]:
                self.check_param_num(1)
                result = self.cns_service.query_cns_by_name(self._args[0])
                Precompile.print_cns_info(result)
                return
            # query cns information by name and version
            if self._cmd == self.functions["cns"][2]:
                self.check_param_num(2)
                result = self.cns_service.query_cns_by_nameAndVersion(self._args[0], self._args[1])
                Precompile.print_cns_info(result)
                return
        except ArgumentsError:
            self.print_cns_usage()

    def call_consensus(self):
        """
        call consensusPrecompile
        addSealer(string nodeID) public returns(int256)
        addObserver(string nodeID) public returns(int256)
        remove(string nodeID) public returns(int256)
        """
        if self._cmd not in self.functions["consensus"]:
            return
        self.consensus_precompile = ConsensusPrecompile(self._contract_path)
        try:
            self.check_param_num(1)
            # addSealer
            if self._cmd == self.functions["consensus"][0]:
                self.consensus_precompile.addSealer(self._args[0])
            # addObserver
            elif self._cmd == self.functions["consensus"][1]:
                self.consensus_precompile.addObserver(self._args[0])
            # removeNode
            elif self._cmd == self.functions["consensus"][2]:
                self.consensus_precompile.removeNode(self._args[0])
            self.print_succ_msg()
        except TransactionException as e:
            self.print_transaction_exception(e)
        except ArgumentsError:
            self.print_consensus_usage()

    def call_sysconfig_precompile(self):
        """
        call sysconfig precompile
        function setSystemConfigByKey(string key, string value) public returns(int256)
        """
        if self._cmd not in self.functions["sysconfig"]:
            return
        self.config_precompile = ConfigPrecompile(self._contract_path)
        try:
            # setSystemConfigByKey
            if self._cmd == self.functions["sysconfig"][0]:
                self.check_param_num(2)
                self.config_precompile.setValueByKey(self._args[0], self._args[1])
                self.print_succ_msg()
        except TransactionException as e:
            self.print_transaction_exception(e)
        except ArgumentsError:
            self.print_sysconfig_usage()

    def exec_grant_cmd(self, index=0):
        """
        exec_grant_cmd
        """
        index = 0
        # grantUserTableManager
        if self._cmd == self.functions["permission"][index]:
            self.check_param_num(2)
            self.premisson_service.grantUserTableManager(self._args[0], self._args[1])
        index = index + 1
        # grantPermissionManager
        if self._cmd == self.functions["permission"][index]:
            self.check_param_num(1)
            self.premisson_service.grantPermissionManager(self._args[0])
        index = index + 1
        # grantNodeManager
        if self._cmd == self.functions["permission"][index]:
            self.check_param_num(1)
            self.premisson_service.grantNodeManager(self._args[0])
        index = index + 1
        # grantCNSManager
        if self._cmd == self.functions["permission"][index]:
            self.check_param_num(1)
            self.premisson_service.grantCNSManager(self._args[0])
        index = index + 1
        # grantSysConfigManager
        if self._cmd == self.functions["permission"][index]:
            self.check_param_num(1)
            self.premisson_service.grantSysConfigManager(self._args[0])
        index = index + 1
        return index

    def exec_revoke_cmd(self, index):
        """
        execute revoke cmds
        """
        # revokeUserTableManager
        if self._cmd == self.functions["permission"][index]:
            self.check_param_num(2)
            self.premisson_service.revokeUserTableManager(self._args[0], self._args[1])
        index = index + 1
        # revokeDeployAndCreateManager
        if self._cmd == self.functions["permission"][index]:
            self.check_param_num(2)
            self.premisson_service.revokeDeployAndCreateManager(self._args[0], self._args[1])
        index = index + 1
        # revokePermissionManager
        if self._cmd == self.functions["permission"][index]:
            self.check_param_num(1)
            self.premisson_service.revokePermissionManager(self._args[0])
        index = index + 1
        # revokeNodeManager
        if self._cmd == self.functions["permission"][index]:
            self.check_param_num(1)
            self.premisson_service.revokeNodeManager(self._args[0])
        index = index + 1
        # revokeCNSManager
        if self._cmd == self.functions["permission"][index]:
            self.check_param_num(1)
            self.premisson_service.revokeCNSManager(self._args[0])
        index = index + 1
        # revokeSysConfigManager
        if self._cmd == self.functions["permission"][index]:
            self.check_param_num(1)
            self.premisson_service.revokeSysConfigManager(self._args[0])
        index = index + 1
        return index

    def exec_list_cmd(self, index):
        """
        execute list cmds
        """
        # listUserTableManager
        if self._cmd == self.functions["permission"][index]:
            self.premisson_service.listUserTableManager()
        index = index + 1
        # listDeployAndCreateManager
        if self._cmd == self.functions["permission"][index]:
            self.premisson_service.listDeployAndCreateManager()
        index = index + 1
        # listPermissionManager
        if self._cmd == self.functions["permission"][index]:
            self.premisson_service.listPermissionManager()
        index = index + 1
        # listNodeManager
        if self._cmd == self.functions["permission"][index]:
            self.premisson_service.listNodeManager()
        index = index + 1
        # listCNSManager
        if self._cmd == self.functions["permission"][index]:
            self.premisson_service.listCNSManager()
        index = index + 1
        # listSysConfigManager
        if self._cmd == self.functions["permission"][index]:
            self.premisson_service.listSysConfigManager()
        index = index + 1
        return index

    def exec_permission_cmd(self):
        """
        execute permission cmd
        """
        index = self.exec_grant_cmd()
        index = self.exec_revoke_cmd(index)
        self.exec_list_cmd(index)

    def call_permission_precompile(self):
        """
        call permission precompile
        """
        if self._cmd not in self.functions["permission"]:
            return
        self.premisson_service = PermissionService(self._contract_path)
        try:
            self.exec_permission_cmd()
            self.print_succ_msg()
        except TransactionException as e:
            self.print_transaction_exception(e)
        except PrecompileError as e:
            self.print_error_msg(e)
        except ArgumentsError:
            self.print_permission_usage()
