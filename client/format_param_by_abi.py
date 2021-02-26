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
  @author: kentzhang
  @date: 2021-02
'''

from collections import Iterable

from client.bcoserror import ArgumentsError
from eth_utils import to_checksum_address


def remove_pre_su_fix(item: str):
    item = item.strip(" ")
    item = item.rstrip(" ")
    item = item.strip("'")
    item = item.rstrip("'")
    item = item.strip("\"")
    item = item.rstrip("\"")
    return item


def parse_input_array_str(inputstr: str):
    # 用json解析有点问题，命令行输入json时，会转换掉"双引号，所以自行实现
    inputstr = remove_pre_su_fix(inputstr)
    inputstr = inputstr.strip("[")
    inputstr = inputstr.rstrip("]")
    tempitems = inputstr.split(",")
    stritems = []
    for item in tempitems:
        item = remove_pre_su_fix(item)
        stritems.append(item)
    return stritems


def format_single_param(param, abitype):
    # 默认是string
    fmt_res = param
    # print(type(param))
    if "int" in abitype or "int256" in abitype:
        if not isinstance(param, int):
            fmt_res = int(param, 10)
    if "address" in abitype:
        try:
            fmt_res = to_checksum_address(param)
        except ArgumentsError as e:
            raise ArgumentsError(("ERROR >> covert {} to to_checksum_address failed,"
                                  " exception: {}").format(param, e))
    if "bytes" in abitype:
        try:
            fmt_res = bytes(param, "utf-8")
        except Exception as e:
            raise ArgumentsError(
                "ERROR >> parse {} to bytes failed, error info: {}".format(param, e))
    if "bool" in abitype:
        # 有可能是string或已经是bool类型了，判断下
        if isinstance(param, str):
            if "TRUE" == param.upper():
                fmt_res = True
            elif "FALSE" == param.upper():
                fmt_res = False
            else:
                raise ArgumentsError(
                    "ERROR >> format bool type failed, WRONG param: {}".format(param))
    return fmt_res


def format_array_args_by_abi(input_param, abitype):
    # abi类型类似address[],string[],int256[]
    # 参数类似['0x111','0x2222'],[1,2,3],['aaa','bbb','ccc']

    paramarray = parse_input_array_str(input_param)
    resarray = []
    # print(paramarray)
    for param in paramarray:
        fmt_res = format_single_param(param, abitype)
        resarray.append(fmt_res)
    return resarray


def is_array_param(abittype):
    if abittype.endswith("[]"):
        return True
    return False


def format_args_by_function_abi(inputparams, inputabi):
    paramformatted = []
    index = -1
    if len(inputparams) != len(inputabi):
        raise ArgumentsError(("Invalid Arguments {}, expected params size: {},"
                              " inputted params size: {}".format(inputparams,
                                                                 len(inputabi),
                                                                 len(inputparams))))

    for abi_item in inputabi:
        index += 1
        param = inputparams[index]
        if param is None:
            continue
        if isinstance(param, Iterable) is False:
            paramformatted.append(param)
            continue
        abitype = abi_item["type"]
        if is_array_param(abitype):
            # print("is Array")
            param = format_array_args_by_abi(param, abitype)
            paramformatted.append(param)
            continue
        if '\'' in param:
            param = param.replace('\'', "")
        param = format_single_param(param, abitype)
        paramformatted.append(param)
    return paramformatted


doTest = False
if doTest:
    # 数组参数需要加上中括号，比如[1, 2, 3]，数组中是字符串或字节类型，加双引号，例如[“alice”, ”bob”]，注意数组参数中不要有空格；布尔类型为true或者false。
    strarrayparam = "[\"aaa\",\"bbb\",\"ccc\"]"
    intarrayparam = "[1,2,3]"
    boolarrayparam = "[true,true,false]"
    boolstrarrayparam = "[\"True\",\"false\",\"true\"]"
    addrarrayparam = "[\"0x7029c502b4f824d19bd7921e9cb74ef92392fb1b\"," \
                     "\"0x9029c502b4f824d19bd7921e9cb74ef92392fb1b\"," \
                     "\"0xa029c502b4f824d19bd7921e9cb74ef92392fb1b\"]"
    res = format_array_args_by_abi(addrarrayparam, "address[]")
    print(res)
    res = format_array_args_by_abi(intarrayparam, "int256[]")
    print(res)
    res = format_array_args_by_abi(strarrayparam, "string[]")
    print(res)
    res = format_array_args_by_abi(boolarrayparam, "bool[]")
    print(res)
    res = format_array_args_by_abi(boolstrarrayparam, "bool[]")
    print(res)

    from client.datatype_parser import DatatypeParser

    parser = DatatypeParser("contracts/NoteGroup.abi")
    fn_abi = parser.get_function_inputs_abi("set_addr")
    fmt_args = format_args_by_function_abi([addrarrayparam, "testing"], fn_abi)
    print(fmt_args)
