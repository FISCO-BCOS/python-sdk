'''
  bcosliteclientpy is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/)
  bcosliteclientpy is free software: you can redistribute it and/or modify it under the
  terms of the MIT License as published by the Free Software Foundation. This project is
  distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Thanks for
  authors and contributors of eth-abi, eth-account, eth-hash，eth-keys, eth-typing, eth-utils,
  rlp, eth-rlp , hexbytes ... and relative projects
  @file: crud_service.py
  @function:
  @author: yujiechen
  @date: 2019-07
'''
import json
from client.common import transaction_common
from client.precompile.crud.condition import Condition
from client.bcoserror import PrecompileError


class PrecompileGlobalConfig:
    """
    global values
    """

    def __init__(self):
        self.SYS_TABLE = "_sys_tables_"
        self.USER_TABLE_PREFIX = "_user_"
        self.SYS_TABLE_ACCESS = "_sys_table_access_"
        self.SYS_CONSENSUS = "_sys_consensus_"
        self.SYS_CNS = "_sys_cns_"
        self.SYS_CONFIG = "_sys_config_"


class Entry:
    """
    define Entry
    """

    def __init__(self):
        self._fields = {}

    def get(self, key):
        """
        get value according to key
        """
        return self._fields[key]

    def put(self, key, value):
        """
        set <key, value> into the field
        """
        self._fields[key] = value

    def get_fields(self):
        return self._fields


class Table:
    """
    define Table
    """

    def __init__(self, table_name, table_key, table_fields, optional=None):
        """
        init table name and table key
        """
        self._table_name = table_name
        self._table_key = table_key
        self._table_fields = table_fields
        self._optional = optional

    def get_table_name(self):
        return self._table_name

    def get_table_key(self):
        return self._table_key

    def get_table_fields(self):
        return self.get_table_fields

    def get_optional(self):
        return self._optional

    def getEntry(self):
        """
        new entry
        """
        return Entry()

    def get_condition(self):
        """
        new Condition
        """
        return Condition()


class CRUDService:
    """
    implementation of CRUDService
    """

    def __init__(self, contract_path):
        """
        init precompile address for TableFactory precompile and CRUDPrecompile
        """
        self.tableFactory_address = "0x0000000000000000000000000000000000001001"
        self.crud_address = "0x0000000000000000000000000000000000001002"
        self.contract_path = contract_path
        self.client = transaction_common.TransactionCommon(
            self.crud_address, contract_path, "TableFactory")
        self.tableFactory_client = transaction_common.TransactionCommon(
            self.tableFactory_address, contract_path, "CRUD")

    def __del__(self):
        """
        finish the client
        """
        self.client.finish()
        self.tableFactory_client.finish()

    def define_const(self):
        """
        define const value for CURD
        """
        self._max_table_key_len = 255

    # interface releated to TableFactory
    def create_table(self, table):
        """
        function createTable(string, string, string) public returns (int)
        """
        fn_name = "createTable"
        fn_args = [table.get_table_name(), table.get_table_key(), table.get_table_fields()]
        return self.tableFactory_client.send_transaction_getReceipt(fn_name, fn_args)

    def check_key_length(self, key):
        """
        check key length
        """
        if len(key) >= self._max_table_key_len:
            raise Exception('''The value of the table key exceeds
                            the maximum limit {}'''.
                            format(self._max_table_key_len))

    def insert(self, table, entry):
        """
        insert(string tableName, string key, string entry,
               string optional)
        """
        self.check_key_length(table.get_table_key())
        fn_name = "insert"
        fn_args = [table.get_table_name(), table.get_table_key(), json.dump(entry.get_fields())]
        return self.client.send_transaction_getReceipt(fn_name, fn_args)

    def update(self, table, entry, condition):
        """
        function update(string tableName, string key, string entry,
                string condition, string optional) public returns(int);
        """
        self.check_key_length(table.get_table_key())
        fn_name = "update"
        fn_args = [table.get_table_name(), table.get_table_key(),
                   json.dump(entry.get_fields()), json.dumps(condition.get_conditions()),
                   table.get_optional()]
        return self.client.send_transaction_getReceipt(fn_name, fn_args)

    def remove(self, table, condition):
        """
        function remove(string tableName, string key,
                    string condition, string optional) public returns(int);
        """
        self.check_key_length(table.get_table_key())
        fn_name = "remove"
        fn_args = [table.get_table_name(), table.get_table_key(),
                   json.dumps(condition.get_conditions()), table.get_optional()]
        return self.client.send_transaction_getReceipt(fn_name, fn_args)

    def select(self, table, condition):
        """
        function select(string tableName, string key, string condition,
                 string optional) public constant returns(string)
        """
        self.check_key_length(table.get_table_key())
        fn_name = "select"
        fn_args = [table.get_table_name(), table.get_table_key(), json.dumps(
            condition.get_conditions()), table.get_optional()]
        return self.client.call_and_decode(self.cns_abi_path, fn_name, fn_args)

    def desc(self, table_name):
        self.check_key_length(table_name)
        table = Table(PrecompileGlobalConfig.SYS_TABLE,
                      PrecompileGlobalConfig.USER_TABLE_PREFIX + table_name, "")
        condition = table.get_condition()
        user_table = self.select(table, condition)
        if not user_table.strip():
            return Table(table_name, user_table[0]["key_field"], user_table[0]["value_field"])
        else:
            raise PrecompileError("The table {} doesn't exits!".format(table_name))
