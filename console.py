#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-
'''
  bcosliteclientpy is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/)
  bcosliteclientpy is free software: you can redistribute it and/or modify it under the
  terms of the MIT License as published by the Free Software Foundation. This project is
  distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Thanks for
  authors and contributors of eth-abi, eth-account, eth-hash，eth-keys, eth-typing, eth-utils,
  rlp, eth-rlp , hexbytes ... and relative projects
  @author: kentzhang
  @date: 2019-06
'''
import argparse
import sys
import glob
from client.stattool import StatTool
from client_config import client_config
from eth_account.account import (
    Account
)
from eth_utils.hexadecimal import encode_hex
from client.bcosclient import (
    BcosClient
)
from client.contractnote import ContractNote
import json
import os
from client.datatype_parser import DatatypeParser
from eth_utils import to_checksum_address
from console_utils.precompile import Precompile
from client.common import transaction_common
from client.common import common
from client.bcoserror import BcosError, CompileError, PrecompileError, ArgumentsError, BcosException
from client.common.transaction_exception import TransactionException
import argcomplete


# --------------------------------------------------------------------------------------------
# useful functions
# --------------------------------------------------------------------------------------------


def default_abi_file(contractname):
    abi_file = contractname
    if not abi_file.endswith(".abi"):  # default from contracts/xxxx.abi,if only input a name
        abi_file = contracts_dir + "/" + contractname + ".abi"
    return abi_file


def fill_params(params, paramsname):
    index = 0
    result = dict()
    for name in paramsname:
        result[name] = params[index]
        index += 1
    return result


def print_receipt_logs_and_txoutput(client, receipt, contractname, parser=None):
    print("\nINFO >>  receipt logs : ")
    # 解析receipt里的log
    if parser is None and len(contractname) > 0:
        parser = DatatypeParser(default_abi_file(contractname))
    logresult = parser.parse_event_logs(receipt["logs"])
    i = 0
    for log in logresult:
        if 'eventname' in log:
            i = i + 1
            print("{}): log name: {} , data: {}".format(i, log['eventname'], log['eventdata']))
    txhash = receipt["transactionHash"]
    txresponse = client.getTransactionByHash(txhash)
    inputdetail = print_parse_transaction(txresponse, "", parser)
    # 解析该交易在receipt里输出的output,即交易调用的方法的return值
    outputresult = parser.parse_receipt_output(inputdetail['name'], receipt['output'])
    print("receipt output :", outputresult)


def format_args_by_abi(inputparams, inputabi):
    paramformatted = []
    index = -1
    # print(inputabi)
    # print(inputparams)
    for input in inputabi:
        # print(input)
        index += 1
        param = inputparams[index]
        if '\'' in param:
            param = param.replace('\'', "")
        if "int" in input["type"]:
            paramformatted.append(int(param, 10))
            continue
        # print(input)
        if "address" in input["type"]:
            print("to checksum address ", param)
            try:
                paramformatted.append(to_checksum_address(param))
            except Exception as e:
                print(("ERROR >> covert {} to to_checksum_address failed,"
                       " exception: {}").format(param, e))
                sys.exit(1)
            continue
        paramformatted.append(param)
    return paramformatted


def format_args_by_types(inputparams, types):
    index = -1
    newparam = []
    # print(types)
    for type in types:
        index += 1
        v = inputparams[index]
        if type == "str":
            if '\'' in v:
                v = v.replace('\'', '')
            newparam.append(v)
            continue
        if type == "hex":
            value = int(v, 10)
            if value > BcosClient.max_block_number or value < 0:
                raise ArgumentsError(("invalid input interger: {},"
                                      " must between 0 and {}").format(value,
                                                                       BcosClient.max_block_number))
            newparam.append(hex(value))
            continue
        if type == "bool":
            if v.lower() == "true":
                newparam.append(True)
            else:
                newparam.append(False)

            continue
    # print(newparam)
    return newparam


def print_parse_transaction(tx, contractname, parser=None):
    if parser is None:
        parser = DatatypeParser(default_abi_file(contractname))
    inputdata = tx["input"]
    inputdetail = parser.parse_transaction_input(inputdata)
    print("INFO >> transaction hash : ", tx["hash"])
    print("tx input data detail:\n {}".format(inputdetail))
    return (inputdetail)


def check_result(result):
    """
    check result
    """
    if isinstance(result, dict) and 'error' in result.keys():
        return True
    return False


def get_validcmds():
    """
    get valid cmds
    """
    validcmds = ["showaccount", "newaccount", "deploy", "call",
                 "sendtx", "list", "int", "txinput", "checkaddr", "usage"]
    return validcmds


def common_cmd():
    """
    common cmd
    """
    # --------------------------------------------------------------------------------------------
    # console cmd entity
    # --------------------------------------------------------------------------------------------
    # 用比较通用的方式处理所有getXXX接口，处理少量特例
    getcmds = dict()
    getcmds["getNodeVersion"] = []
    getcmds["getBlockNumber"] = []
    getcmds["getPbftView"] = []
    getcmds["getSealerList"] = []
    getcmds["getObserverList"] = []
    getcmds["getConsensusStatus"] = []
    getcmds["getSyncStatus"] = []
    getcmds["getPeers"] = []
    getcmds["getGroupPeers"] = []
    getcmds["getNodeIDList"] = []
    getcmds["getGroupList"] = []
    getcmds["getBlockByHash"] = [["str", "bool"],
                                 ("hash : 区块Hash(hash string), "
                                  "是否查询交易数据(true/false for with transaction data)")]
    getcmds["getBlockByNumber"] = [["hex", "bool"],
                                   ("number bool : 区块高度(number), "
                                    "是否查询交易数据(true/false for with transaction data)")]
    getcmds["getBlockHashByNumber"] = [["hex"], "number : 区块高度(number)"]
    getcmds["getTransactionByHash"] = [["str"], "hash : 交易Hash(hash string)"]
    getcmds["getTransactionByBlockHashAndIndex"] = [["str", "hex"],
                                                    ("blockhash index :"
                                                     " 区块Hash(hash string), 交易在区块里的位置(index)")]
    getcmds["getTransactionByBlockNumberAndIndex"] = [
        ["hex", "hex"], "blocknumber index : 区块高度(number),交易在区块里的位置(index)"]
    getcmds["getTransactionReceipt"] = [["str"], "hash: 交易hash(hash string)"]
    getcmds["getPendingTransactions"] = []
    getcmds["getPendingTxSize"] = []
    getcmds["getCode"] = ["str"]
    getcmds["getTotalTransactionCount"] = []
    getcmds["getSystemConfigByKey"] = [["str"], ("name : 配置参数名"
                                                 "(system param name),eg:tx_count_limit")]
    return getcmds


def check_cmd(cmd, validcmds, common_cmd):
    if (cmd not in validcmds) and (cmd not in common_cmd):
        print("console cmd  [{}]  not implement yet,see the usage\n".format(cmd))
        return False
    return True


def printusage(usagemsg, precompile=None):
    """
    print usage
    """
    print('''usage
        使用说明,输入python console.py [指令 参数列表]
        Usage of console (FISCO BCOS 2.0 lite client @python):
        python console.py [cmd args]
        ''')
    index = 0
    for msg in usagemsg:
        index += 1
        print("{}): {}\n".format(index, msg))
    if precompile is None:
        return
    precompile.print_cns_usage(True)
    precompile.print_consensus_usage(True)
    precompile.print_sysconfig_usage(True)
    precompile.print_all_permission_usage()


def usage(client_config):
    """
    generate usage list
    """
    usagemsg = []
    usagemsg.append(('''newaccount [name] [password] [save]
        创建一个新帐户，参数为帐户名(如alice,bob)和密码
        结果加密保存在配置文件指定的帐户目录 *如同目录下已经有同名帐户文件，旧文件会复制一个备份
        如输入了"save"参数在最后，则不做询问直接备份和写入
        create a new account ,save to :[{}] (default) ,
        the path in client_config.py:[account_keyfile_path]
        if account file has exist ,then old file will save to a backup
        if "save" arg follows,then backup file and write new without ask''')
                    .format(client_config.account_keyfile_path))
    usagemsg.append('''showaccount [name] [password]
        指定帐户名字(不带后缀)和密码，打开配置文件里默认账户文件路径下的[name].keystore文件，打印公私钥和地址
        ''')
    usagemsg.append('''deploy [contract_binary_file] [save]
        部署合约,合约来自编译后的bin文件（部署命令为了审慎起见，需要指定bin文件的全路径）。
        如给出'save'参数，新地址会写入本地记录文件
        ndeploy contract from a binary file,eg: deploy contracts/SimpleInfo.bin
        if 'save' in args, so save address to file''')

    usagemsg.append('''call [contractname] [address] [func]  [args...]
        call合约的一个只读接口,解析返回值
        call a constant function of contract and get the returns
        eg: call SimpleInfo 0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC getbalance1 11
        if address is "last" ,then load last address from :{}
        eg: call SimpleInfo last getall
        '''.format(client_config.contract_info_file))

    usagemsg.append('''sendtx [contractname]  [address] [func] [args...]
        发送交易调用指定合约的接口，交易如成功，结果会写入区块和状态
        send transaction,will commit to blockchain if success
        eg: sendtx SimpleInfo 0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC
        set alice 100 0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC
        if address is "last" ,then load last address from :{}
        eg: sendtx SimpleInfo last set 'test' 100 '0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC'
        '''.format(client_config.contract_info_file))

    usagemsg.append('''all the 'get' command for JSON RPC
        各种get接口，查询节点的各种状态（不一一列出，可用list指令查看接口列表和参数名）
        neg: [getBlockByNumber 10 true].
        use 'python console.py list' to show all get cmds ''')

    usagemsg.append('''list
        列出所有支持的get接口名和参数
        list: list all  getcmds  has implemented
        (getBlock...getTransaction...getReceipt..getOthers)''')

    usagemsg.append('''int [hex number]
        输入一个十六进制的数字，转为十进制（考虑到json接口里很多数字都是十六进制的，所以提供这个功能）
        convert a hex str to int ,eg: int 0x65''')

    usagemsg.append('''txinput [contractname] [inputdata(in hex string)]
        复制一段来自transaction的inputdata(十六进制字符串)，指定合约名，则可以自动解析（合约的abi文件应存在指定目录下）
        parse the transaction input data by  contractname，eg: txinput SimpleInfo [txinputdata]''')

    usagemsg.append('''checkaddr [address]
        将普通地址转为自校验地址,自校验地址使用时不容易出错
        change address to checksum address according EIP55:
        to_checksum_address: 0xf2c07c98a6829ae61f3cb40c69f6b2f035dd63fc
        -> 0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC
        ''')
    return usagemsg


def get_functions_by_contract(contract_name):
    """
    get functions according to contract_name
    """
    data_parser = DatatypeParser(default_abi_file(contract_name))
    return [*data_parser.func_abi_map_by_name.keys()]


def list_address(contract_name):
    """
    get address according to contract_name
    """
    return ContractNote.get_contract_addresses(contract_name)


def list_api(file_pattern):
    """
    return list according to file_pattern
    """
    file_list = [f for f in glob.glob(file_pattern)]
    targets = []
    for file in file_list:
        targets.append(os.path.basename(file).split(".")[0])
    return targets


def list_contracts():
    """
    list all contractname for call
    """
    return list_api(contracts_dir + "/*.sol")


def list_accounts():
    """
    list all accounts
    """
    return list_api("bin/accounts/*.keystore")


# get supported command
validcmds = get_validcmds()
getcmds = common_cmd()
Precompile.define_functions()
validcmds = validcmds + Precompile.get_all_cmd()
allcmds = validcmds + [*getcmds.keys()]
contracts_dir = "contracts"


def completion(prefix, parsed_args, **kwargs):
    """
    complete the shell
    """
    if parsed_args.cmd is None:
        return allcmds
    # deploy contract
    if parsed_args.cmd[0] == "deploy":
        return list_contracts()

    # call and sendtx
    # warn(parsed_args)
    if parsed_args.cmd[0] == "call" or parsed_args.cmd[0] == "sendtx":
        # only list the contract name
        if len(parsed_args.cmd) == 1:
            return list_contracts()
        # list the contract address
        if len(parsed_args.cmd) == 2:
            return list_address(parsed_args.cmd[1])
        # list functions
        if len(parsed_args.cmd) == 3:
            return get_functions_by_contract(parsed_args.cmd[1])

    # call showaccount
    if parsed_args.cmd[0] == "showaccount":
        return list_accounts()

    # registerCNS [contract_name] [contract_address] [contract_version]
    if parsed_args.cmd[0] == "registerCNS":
        # list contract name
        if len(parsed_args.cmd) == 1:
            return list_contracts()
        # list contract address
        if len(parsed_args.cmd) == 2:
            return list_address(parsed_args.cmd[1])
    # queryCNSByName [contract_name]
    if parsed_args.cmd[0] == "queryCNSByName":
        # list contract name
        if len(parsed_args.cmd) == 1:
            return list_contracts()
    # queryCNSByNameAndVersion [contract_name] [contract_version]
    if parsed_args.cmd[0] == "queryCNSByNameAndVersion":
        if len(parsed_args.cmd) == 1:
            return list_contracts()
    # sysconfig
    if parsed_args.cmd[0] == "setSystemConfigByKey" or parsed_args.cmd[0] == "getSystemConfigByKey":
        return ["tx_count_limit", "tx_gas_limit"]
    return []


def parse_commands(argv):
    """
    parse the input command
    """
    # 首先创建一个ArgumentParser对象
    parser = argparse.ArgumentParser(description='FISCO BCOS 2.0 lite client @python')
    parsed_args = argparse.Namespace()
    cmd = parser.add_argument('cmd', nargs="+",       # 添加参数
                              help='the command for console')
    cmd.completer = completion

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    print("\nINFO >> user input : {}\n".format(args.cmd))
    cmd = args.cmd[0]
    inputparams = args.cmd[1:]
    return cmd, inputparams


def print_error_msg(cmd, e):
    """
    print error msg
    """
    print("ERROR >> execute {} failed\nERROR >> error information: {}\n".format(cmd, e))


def print_info(level, cmd):
    """
    print information
    """
    print("{} >> {}".format(level, cmd))


def main(argv):
    usagemsg = usage(client_config)
    cmd, inputparams = parse_commands(argv)
    precompile = Precompile(cmd, inputparams, contracts_dir + "/precompile")

    # check cmd
    valid = check_cmd(cmd, validcmds, getcmds)
    if valid is False:
        printusage(usagemsg, precompile)
        return
    try:
        client = BcosClient()
        # ---------------------------------------------------------------------------
        # start command functions

        # --------------------------------------------------------------------------------------------
        # console cmd entity
        # --------------------------------------------------------------------------------------------

        # try to callback cns precompile
        precompile.call_cns()
        # try to callback consensus precompile
        precompile.call_consensus()
        # try to callback config precompile
        precompile.call_sysconfig_precompile()
        # try to callback permission precompile
        precompile.call_permission_precompile()
        # try to callback crud precompile
        precompile.call_crud_precompile()
        if cmd == 'showaccount':
            # must be 2 params
            common.check_param_num(inputparams, 2, True)
            name = inputparams[0]
            password = inputparams[1]
            keyfile = "{}/{}.keystore".format(client_config.account_keyfile_path, name)
            # the account doesn't exists
            if os.path.exists(keyfile) is False:
                raise BcosException("account {} doesn't exists".format(name))
            print("show account : {}, keyfile:{} ,password {}  ".format(name, keyfile, password))
            try:
                with open(keyfile, "r") as dump_f:
                    keytext = json.load(dump_f)
                    stat = StatTool.begin()
                    privkey = Account.decrypt(keytext, password)
                    stat.done()
                    print("decrypt use time : %.3f s" % (stat.time_used))
                    ac2 = Account.from_key(privkey)
                    print("address:\t", ac2.address)
                    print("privkey:\t", encode_hex(ac2.key))
                    print("pubkey :\t", ac2.publickey)
                    print("\naccount store in file: [{}]".format(keyfile))
                    print("\n**** please remember your password !!! *****")
            except Exception as e:
                raise BcosException(("load account info for [{}] failed,"
                                     " error info: {}!").format(name, e))

        if cmd == 'newaccount':
            common.check_param_num(inputparams, 2, True)
            name = inputparams[0]
            if len(name) > 254:
                print_info("WARNING", "account name should no more than 245")
                sys.exit(1)
            password = inputparams[1]
            print("starting : {} {} ".format(name, password))
            ac = Account.create(password)
            print("new address :\t", ac.address)
            print("new privkey :\t", encode_hex(ac.key))
            print("new pubkey :\t", ac.publickey)

            stat = StatTool.begin()
            kf = Account.encrypt(ac.privateKey, password)
            stat.done()
            print("encrypt use time : %.3f s" % (stat.time_used))
            keyfile = "{}/{}.keystore".format(client_config.account_keyfile_path, name)
            print("save to file : [{}]".format(keyfile))
            forcewrite = False
            if not os.access(keyfile, os.F_OK):
                forcewrite = True
            else:
                # old file exist,move to backup file first
                if(len(inputparams) == 3 and inputparams[2] == "save"):
                    forcewrite = True
                else:
                    forcewrite = common.backup_file(keyfile)
            if forcewrite:
                with open(keyfile, "w") as dump_f:
                    json.dump(kf, dump_f)
                    dump_f.close()
            print(">>-------------------------------------------------------")
            print(
                "INFO >> read [{}] again after new account,address & keys in file:".format(keyfile))
            with open(keyfile, "r") as dump_f:
                keytext = json.load(dump_f)
                stat = StatTool.begin()
                privkey = Account.decrypt(keytext, password)
                stat.done()
                print("decrypt use time : %.3f s" % (stat.time_used))
                ac2 = Account.from_key(privkey)
                print("address:\t", ac2.address)
                print("privkey:\t", encode_hex(ac2.key))
                print("pubkey :\t", ac2.publickey)
                print("\naccount store in file: [{}]".format(keyfile))
                print("\n**** please remember your password !!! *****")
                dump_f.close()

        # --------------------------------------------------------------------------------------------
        # console cmd entity
        # --------------------------------------------------------------------------------------------
        if cmd == "deploy":
            '''deploy abi bin file'''
            if len(inputparams) > 2:
                raise ArgumentsError(("deploy failed, expected at most 2 params,"
                                      " provided: {}").format(len(inputparams)))
            # must be at most 2 params
            common.check_param_num(inputparams, 1, False)
            contractname = inputparams[0].strip()
            trans_client = transaction_common.TransactionCommon("", contracts_dir, contractname)
            result = trans_client.send_transaction_getReceipt(None, None, True)

            print("deploy result  for [{}] is:\n {}".format(
                contractname, json.dumps(result, indent=4)))
            name = contractname
            address = result['contractAddress']
            blocknum = int(result["blockNumber"], 16)
            ContractNote.save_contract_address(name, address)
            print("on block : {},address: {} ".format(blocknum, address))
            if len(inputparams) == 2:
                if inputparams[1] == "save":
                    ContractNote.save_address(name, address, blocknum)
                    print("address save to file: ", client_config.contract_info_file)
            else:
                print(
                    '''\nNOTE : if want to save new address as last
                    address for (call/sendtx)\nadd 'save' to cmdline and run again''')

        # --------------------------------------------------------------------------------------------
        # console cmd entity
        # --------------------------------------------------------------------------------------------
        if cmd == "call" or cmd == "sendtx":
            common.check_param_num(inputparams, 3)
            paramsname = ["contractname", "address", "func"]
            params = fill_params(inputparams, paramsname)
            contractname = params["contractname"]
            address = params["address"]
            if address == "last":
                address = ContractNote.get_last(contractname)
                if address is None:
                    sys.exit("can not get last address for [{}],break;".format(contractname))

            tx_client = transaction_common.TransactionCommon(
                params["address"], contracts_dir, contractname)
            fn_name = params["func"]
            fn_args = inputparams[3:]
            print("INFO >> {} {} , address: {}, func: {}, args:{}"
                  .format(cmd, contractname, address, fn_name, fn_args))
            if cmd == "call":
                result = tx_client.call_and_decode(fn_name, fn_args)
                print("INFO >> {} result: {}".format(cmd, ''.join(result)))
            if cmd == "sendtx":
                receipt = tx_client.send_transaction_getReceipt(fn_name, fn_args)
                data_parser = DatatypeParser(default_abi_file(contractname))
                # 解析receipt里的log 和 相关的tx ,output
                print_receipt_logs_and_txoutput(client, receipt, "", data_parser)

        # --------------------------------------------------------------------------------------------
        # console cmd entity
        # --------------------------------------------------------------------------------------------
        if cmd in getcmds:
            types = []
            if len(getcmds[cmd]) > 0:
                types = getcmds[cmd][0]
            if "getBlockBy" in cmd:
                # make a default for getBlockBy...
                if(len(inputparams) == 1):
                    inputparams.append("false")
                    print('''**NOTE >> for getBlockbyNumber/Hash ,
                          missing 2nd arg ,defaut (false) gave :
                          withoud retrieve transactions detail.
                          full command,eg: getBlockByNumber 10 true (or false)\n''')
            try:
                fmtargs = format_args_by_types(inputparams, types)
            except Exception:
                cmdinfo = getcmds[cmd]
                memo = " no args"
                if(len(cmdinfo) == 2):
                    memo = " {} ".format(cmdinfo[1])
                print("WARN >> args not match,should be : {} {},break\n".format(cmd, memo))
                sys.exit("WARN >> please try again...")
            # print("is a get :{},params:{}".format(cmd,fmtargs) )
            params = [client.groupid]
            params.extend(fmtargs)
            # print(params)
            sendcmd = cmd
            if cmd == "getNodeVersion":  # getNodeVersion is a alias for getClientVersion
                sendcmd = "getClientVersion"
            result = client.common_request(sendcmd, params)

            # print the message
            print("INFO >> {} result: {}".format(cmd, json.dumps(result, indent=4)))

            # if error, return directly
            is_error = check_result(result)
            if is_error is True:
                return

            if cmd == "getTransactionReceipt":
                if len(inputparams) == 2:
                    contractname = inputparams[1]
                    print_receipt_logs_and_txoutput(client, result, contractname)

            if cmd == "getBlockNumber":
                print("INFO >> blockNumber:\t{}".format(int(result, 16)))

            # transfer pbftView to Dec
            if cmd == "getPbftView":
                print("INFO >> pbftView:\t{}".format(int(result, 16)))

            if cmd == "getPendingTxSize":
                print("INFO >> pendingTxSize:\t{}".format(int(result, 16)))

            if cmd == "getTotalTransactionCount":
                print("INFO >> getTotalTransactionCount: ")
                print("INFO >> blockNumber:\t{}".format(int(result["blockNumber"], 16)))
                print("INFO >> failedTxSum:\t{}".format(int(result["failedTxSum"], 16)))
                print("INFO >> txSum:\t{}".format(int(result["txSum"], 16)))

            if "getBlockBy" in cmd:
                blocknum = int(result["number"], 16)
                print("INFO >> blocknumber : ", blocknum)
                print("INFO >> blockhash   : ", result["hash"])
            if "getTransactionBy" in cmd:
                # print(inputparams)
                abifile = None
                if len(inputparams) == 3:
                    abifile = inputparams[2]
                if len(inputparams) == 2 and cmd == "getTransactionByHash":
                    abifile = inputparams[1]
                if abifile is not None:
                    print_parse_transaction(result, abifile)

        # --------------------------------------------------------------------------------------------
        # console cmd entity
        # --------------------------------------------------------------------------------------------
        if cmd == "list":
            i = 0
            print("query commands:")
            for cmd in getcmds:
                hint = "无参数(no args)"
                if len(getcmds[cmd]) == 2:
                    hint = getcmds[cmd][1]
                i = i + 1
                print("{} ): {}\t{}".format(i, cmd, hint))
                print("--------------------------------------------------------------------")

        # --------------------------------------------------------------------------------------------
        # console cmd entity
        # --------------------------------------------------------------------------------------------
        if cmd == 'int':
            print(int(inputparams[0], 16))

        # --------------------------------------------------------------------------------------------
        # console cmd entity
        # --------------------------------------------------------------------------------------------
        if cmd == "txinput":
            contractname = inputparams[0]
            inputdata = inputparams[1]
            dataParser = DatatypeParser(default_abi_file(contractname))
            # print(dataParser.func_abi_map_by_selector)
            result = dataParser.parse_transaction_input(inputdata)
            print("\nabifile : ", default_abi_file(contractname))
            print("parse result: {}".format(result))

        # --------------------------------------------------------------------------------------------
        # console cmd entity
        # --------------------------------------------------------------------------------------------
        if cmd == "checkaddr":
            address = inputparams[0]
            result = to_checksum_address(address)
            print("{} -->\n{}".format(address, result))

        # --------------------------------------------------------------------------------------------
        # console cmd entity
        # --------------------------------------------------------------------------------------------
        if cmd == "usage":
            printusage(usagemsg, precompile)

        # --------------------------------------------------------------------------------------------
        # console cmd entity
        # --------------------------------------------------------------------------------------------
        if (cmd not in validcmds) and (cmd not in getcmds):
            printusage(usagemsg, precompile)
            print("console cmd  [{}]  not implement yet,see the usage\n".format(cmd))
    except TransactionException as e:
        print_error_msg(cmd, e)
    except PrecompileError as e:
        print_error_msg(cmd, e)
    except BcosError as e:
        print_error_msg(cmd, e)
    except CompileError as e:
        print_error_msg(cmd, e)
    except ArgumentsError as e:
        print_error_msg(cmd, e)
    except BcosException as e:
        print_error_msg(cmd, e)


if __name__ == "__main__":
    main(sys.argv[1:])
