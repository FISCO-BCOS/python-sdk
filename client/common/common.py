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
import shutil
import time
import os
import json
import subprocess
import re
from eth_utils.hexadecimal import decode_hex
from client_config import client_config
from eth_utils import to_checksum_address
from utils.contracts import get_function_info
from utils.abi import get_fn_abi_types_single
from client.bcoserror import ArgumentsError, BcosException
from eth_abi import decode_single


def backup_file(file_name):
    """
    backup files
    """
    if os.path.isfile(file_name) is False:
        return
    forcewrite = True
    option = "y"
    if client_config.background is False:
        option = input("INFO >> file [{}] exist , continue (y/n): ".format(file_name))
    if (option.lower() == "y"):
        forcewrite = True
    else:
        forcewrite = False
        print("skip write to file: {}".format(file_name))

    # forcewrite ,so do backup job
    if(forcewrite):
        filestat = os.stat(file_name)
        filetime = time.strftime("%Y%m%d%H%M%S", time.localtime(filestat.st_ctime))
        backupfile = "{}.{}".format(file_name, filetime)
        print("backup [{}] to [{}]".format(file_name, backupfile))
        shutil.move(file_name, backupfile)
    return forcewrite


def print_info(level, cmd):
    """
    print information
    """
    print("{} >> {}".format(level, cmd))


def print_result(ret):
    """
    print result
    """
    if isinstance(ret, dict):
        print_info("    ", "{}".format(json.dumps(ret, indent=4)))
    elif isinstance(ret, list):
        if len(ret) > 0:
            for ret_item in ret:
                print_result(ret_item)
        else:
            print_info("    ", "Empty Set")
    else:
        print_info("    ", "{}".format(ret))


def check_and_format_address(address):
    """
    check address
    """
    try:
        formatted_address = to_checksum_address(address)
        return formatted_address
    except Exception as e:
        raise ArgumentsError("invalid address {}, reason: {}"
                             .format(address, e))


def execute_cmd(cmd):
    """
    execute command
    """
    data = subprocess.check_output(cmd.split(), shell=False, universal_newlines=True)
    status = 0
    return (status, data)


def print_error_msg(cmd, e):
    """
    print error msg
    """
    print("ERROR >> execute {} failed\nERROR >> error information: {}\n".format(cmd, e))


max_block_number = pow(2, 63) - 1


def check_int_range(number_str, limit=max_block_number):
    """
    check integer range
    """
    try:
        number = 0
        if isinstance(number_str, str):
            if number_str.startswith("0x"):
                number = int(number_str, 16)
            else:
                number = int(number_str)
        else:
            number = number_str
        if number > limit or number < 0:
            raise ArgumentsError(("invalid input: {},"
                                  " must between 0 and {}").
                                 format(number, limit))
        return number
    except Exception as e:
        raise ArgumentsError("invalid input:{}, error info: {}".format(number, e))


def check_word(word):
    """
    check world
    """
    result = re.findall(r'([0x]*[a-f0-9]*)', word)
    if result[0] != word:
        raise ArgumentsError(("invalid input {},"
                              " must be in 'a-f' or '0-9' or 'A-F'")
                             .format(word))


def check_hash(hash_str):
    """
    check hash
    """
    min_size = 64
    max_size = 66
    if len(hash_str) < min_size or \
        hash_str.startswith("0x") and len(hash_str) < max_size \
            or len(hash_str) > max_size:
        raise BcosException(("invalid hash: {},"
                             "expected len: {} or {}, real len: {}").
                            format(min_size, max_size,
                                   hash_str, len(hash_str)))
    check_word(hash_str)


def check_nodeId(nodeId):
    """
    check nodeId
    """
    nodeId_len = 128
    if len(nodeId) != nodeId_len:
        raise ArgumentsError("invalid nodeId, must be {} bytes".format(nodeId_len))
    check_word(nodeId)


def check_param_num(args, expected, needEqual=False):
    """
    check param num
    """
    if needEqual is False:
        if len(args) < expected:
            raise ArgumentsError(("invalid arguments, expected num >= {},"
                                  "real num: {}").format(expected, len(args)))
    else:
        if len(args) != expected:
            raise ArgumentsError(("invalid arguments, expected num {},"
                                  "real num: {}").format(expected, len(args)))


def parse_output(output, fn_name, contract_abi, args):
    fn_abi, fn_selector, fn_arguments = fn_abi, fn_selector, fn_arguments = get_function_info(
        fn_name, contract_abi, None, args, None)
    fn_output_types = get_fn_abi_types_single(fn_abi, "outputs")
    decoderesult = decode_single(fn_output_types, decode_hex(output))
    return decoderesult
