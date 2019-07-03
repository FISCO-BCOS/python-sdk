'''
  bcosliteclientpy is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/FISCO-BCOS)
  bcosliteclientpy is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Free Software Foundation
  This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE
  Thanks for authors and contributors of eth-abi，eth-account，eth-hash，eth-keys，eth-typing，eth-utils，rlp, eth-rlp , hexbytes ...and relative projects
  @author: kentzhang
  @date: 2019-06
'''
import argparse
import sys
import shutil
import time
from client.stattool import StatTool
from configobj import ConfigObj
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

parser = argparse.ArgumentParser(description='FISCO BCOS 2.0 lite client @python')   # 首先创建一个ArgumentParser对象
parser.add_argument('cmd',    nargs="+" ,       # 添加参数
                    help='the command for console')
usagemsg = []
validcmds = []
args = parser.parse_args()
print("\n>> user input : {}\n".format(args.cmd) )
cmd = args.cmd[0]
inputparams = args.cmd[1:]
contracts_dir = "contracts"

#--------------------------------------------------------------------------------------------
# useful functions
#--------------------------------------------------------------------------------------------
def default_abi_file(contractname):
    abi_file = contractname
    if not abi_file.endswith(".abi"): #default from contracts/xxxx.abi,if only input a name
        abi_file = contracts_dir + "/" + contractname + ".abi"
    return abi_file

def fill_params(params,paramsname):
    index = 0
    result=dict()
    for name in paramsname:
        result[name]=params[index]
        index+=1
    return result
client = BcosClient ()

def print_receipt_logs_and_txoutput(receipt,contractname,parser=None):
    print("\n>>  receipt logs : ")
    # 解析receipt里的log
    if parser == None and len(contractname) > 0:
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

def format_args_by_abi(inputparams,inputabi):
    paramformatted = []
    index=-1
    #print(inputabi)
    #print(inputparams)
    for input in inputabi:
        #print(input)
        index +=1
        param = inputparams[index]
        if '\'' in param:
            param = param.replace('\'',"")
        if "int" in input["type"]:
            paramformatted.append(int(param,10))
            continue
        #print(input)
        if "address" in input["type"]:
            print ("to checksum address ",param)
            paramformatted.append(to_checksum_address(param))
            continue
        paramformatted.append(param)
    print("param formatted by abi:",paramformatted)
    return paramformatted

def format_args_by_types(inputparams,types):
    index = -1;
    newparam=[]
    #print(types)
    for type in types:
        index += 1
        v = inputparams[index]
        if type=="str":
            if '\'' in v:
                v = v.replace('\'','')
            newparam.append(v)
            continue
        if type=="hex":
            newparam.append(hex(int(v,10)))
            continue
        if type=="bool":
            if v.lower()=="true":
                newparam.append(True)
            else:
                newparam.append(False)

            continue
    #print(newparam)
    return newparam


def print_parse_transaction(tx,contractname,parser=None):
    if parser == None:
        parser = DatatypeParser(default_abi_file(contractname) )
    inputdata = tx["input"]
    inputdetail = parser.parse_transaction_input(inputdata)
    print(">> transaction hash : ", tx["hash"])
    print("tx input data detail:\n {}".format(inputdetail))
    return (inputdetail)


#---------------------------------------------------------------------------
#start command functions

#--------------------------------------------------------------------------------------------
# console cmd entity
#--------------------------------------------------------------------------------------------
validcmds.append("newaccount")
usagemsg.append('''newaccount [name] [password] [save]
创建一个新帐户，参数为帐户名(如alice,bob)和密码
结果加密保存在配置文件指定的帐户目录 *如同目录下已经有同名帐户文件，旧文件会复制一个备份
如输入了"save"参数在最后，则不做询问直接备份和写入
create a new account ,save to :[{}] (default) , the path in client_config.py:[account_keyfile_path]
if account file has exist ,then old file will save to a backup
if "save" arg follows,then backup file and write new without ask'''
                .format(client_config.account_keyfile_path))
if cmd == 'newaccount' :
    name=inputparams[0]
    password=inputparams[1]
    print ("starting : {} {} {} ".format(name,name,password))
    ac = Account.create(password)
    print("new address :\t",ac.address)
    print("new privkey :\t",encode_hex(ac.key) )
    print("new pubkey :\t",ac.publickey )

    stat = StatTool.begin()
    kf = Account.encrypt(ac.privateKey, password)
    stat.done()
    print("encrypt use time : %.3f s"%(stat.timeused))
    import json
    keyfile = "{}/{}.keystore".format(client_config.account_keyfile_path,name)
    print("save to file : [{}]".format(keyfile) )
    forcewrite = False
    if not os.access(keyfile, os.F_OK):
        forcewrite = True
    else:
        #old file exist,move to backup file first
        if(len(inputparams)==3 and inputparams[2] == "save"):
            forcewrite = True
        else:
            str = input(">> file [{}] exist , continue (y/n): ".format(keyfile));
            if (str.lower() == "y"):
                forcewrite = True
            else:
                forcewrite = False
                print("SKIP write new account to file,use exists account for [{}]".format(name))
        #forcewrite ,so do backup job
        if(forcewrite):
            filestat = os.stat(keyfile)
            filetime = time.strftime("%Y%m%d%H%M%S", time.localtime(filestat.st_ctime) )
            backupfile = "{}.{}".format(keyfile,filetime)
            print("backup [{}] to [{}]".format(keyfile,backupfile))
            shutil.move(keyfile,backupfile)

    if forcewrite:
        with open(keyfile, "w") as dump_f:
            json.dump(kf, dump_f)
    print(">>-------------------------------------------------------")
    print(">> read [{}] again after new account,address & keys in file:".format(keyfile))
    with open(keyfile, "r") as dump_f:
        keytext = json.load(dump_f)
        stat = StatTool.begin()
        privkey = Account.decrypt(keytext,password)
        stat.done()
        print("decrypt use time : %.3f s"%(stat.timeused))
        ac2 = Account.from_key(privkey)
        print("address:\t",ac2.address)
        print("privkey:\t",encode_hex(ac2.key))
        print("pubkey :\t",ac2.publickey)
        print("\naccount store in file: [{}]".format(keyfile))
        print("\n**** please remember your password !!! *****")


#--------------------------------------------------------------------------------------------
# console cmd entity
#--------------------------------------------------------------------------------------------
validcmds.append("deploy")
usagemsg.append('''deploy [contract_binary_file] [save]
部署合约,合约来自编译后的bin文件（部署命令为了审慎起见，需要指定bin文件的全路径）。如给出'save'参数，新地址会写入本地记录文件
ndeploy contract from a binary file,eg: deploy contracts/SimpleInfo.bin
if 'save' in args, so save addres to file''')
if cmd=="deploy":
    '''deploy abi bin file'''
    abibinfile=inputparams[0]
    with open(abibinfile,"r") as f:
        contractbin = f.read()
    result = client.deploy(contractbin)
    print ("deploy result  for [{}] is:\n {}".format(abibinfile,json.dumps(result,indent=4) ))
    name = contractname = os.path.splitext(os.path.basename(abibinfile))[0]
    address = result['contractAddress']
    blocknum = int(result["blockNumber"],16)
    print("on block : {},address: {} ".format(blocknum,address))
    if len(inputparams) == 2:
        if inputparams[1]=="save":
            ContractNote.save_address(name, address, blocknum)
            print("address save to file: ",client_config.contract_info_file)
    else:
        print("\nNOTE : if want to save new address as last addres for (call/sendtx)\nadd 'save' to cmdline and run again")
    sys.exit(0)


#--------------------------------------------------------------------------------------------
# console cmd entity
#--------------------------------------------------------------------------------------------
validcmds.append("call")
usagemsg.append('''call [contractname] [address] [func]  [args...]
call合约的一个只读接口,解析返回值
call a constant funciton of contract and get the returns
eg: call SimpleInfo 0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC getbalance1 11
if address is "last" ,then load last address from :{}
eg: call SimpleInfo last getall
'''.format(client_config.contract_info_file))
if cmd=="call":
    paramsname = ["contractname", "address", "func"]
    params = fill_params(inputparams,paramsname)
    args = inputparams[len(paramsname):]
    contractname = params["contractname"]
    data_parser = DatatypeParser(default_abi_file(contractname))
    contract_abi = data_parser.contract_abi

    address = params["address"]
    if address=="last":
        address = ContractNote.get_last(contractname)
        if address == None:
            sys.exit("can not get last address for [{}],break;".format(contractname))
    funcname =params["func"]
    inputabi = data_parser.func_abi_map_by_name[funcname]["inputs"]
    args = format_args_by_abi(args,inputabi)
    print ("call {} , address: {}, func: {}, args:{}"
           .format(contractname,address,funcname,args))
    result = client.call(address,contract_abi,funcname,args)
    print("call result: ",result )

#--------------------------------------------------------------------------------------------
# console cmd entity
#--------------------------------------------------------------------------------------------
validcmds.append("sendtx")
usagemsg.append('''sendtx [contractname]  [address] [func] [args...]
发送交易调用指定合约的接口，交易如成功，结果会写入区块和状态
send transaction,will commit to blockchain if success
eg: sendtx SimpleInfo 0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC set alice 100 0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC
if address is "last" ,then load last address from :{}
eg: sendtx SimpleInfo last set 'test' 100 '0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC'
'''.format(client_config.contract_info_file))
if cmd=="sendtx":
    paramsname = ["contractname", "address", "func"]
    params = fill_params(inputparams,paramsname)
    args = inputparams[len(paramsname):]
    contractname = params["contractname"]
    data_parser = DatatypeParser(default_abi_file(contractname))
    contract_abi = data_parser.contract_abi

    address = params["address"]
    if address=="last":
        address = ContractNote.get_last(contractname)
        if address == None:
            sys.exit("\ncan not get last address for [{}],break;\n".format(contractname))
    funcname = params["func"]
   # print("data_parser.func_abi_map_by_name",data_parser.func_abi_map_by_name)
    inputabi = data_parser.func_abi_map_by_name[funcname]["inputs"]
    args = format_args_by_abi(args,inputabi)
    #from eth_utils import to_checksum_address
    #args = ['simplename', 2024, to_checksum_address('0x7029c502b4F824d19Bd7921E9cb74Ef92392FB1c')]
    print ("sendtx {} , address: {}, func: {}, args:{}"
           .format(contractname,address,funcname,args))
    receipt = client.sendRawTransactionGetReceipt(address,contract_abi,params["func"],args)
    print("\n\nsendtx receipt: ",json.dumps(receipt,indent=4) )
    #解析receipt里的log 和 相关的tx ,output
    print_receipt_logs_and_txoutput(receipt,"",data_parser)

#--------------------------------------------------------------------------------------------
# console cmd entity
#--------------------------------------------------------------------------------------------
#用比较通用的方式处理所有getXXX接口，处理少量特例
getcmds=dict()
getcmds["getNodeVersion"]=[]
getcmds["getBlockNumber"]=[]
getcmds["getPbftView"]=[]
getcmds["getSealerList"]=[]
getcmds["getObserverList"]=[]
getcmds["getConsensusStatus"]=[]
getcmds["getSyncStatus"]=[]
getcmds["getPeers"]=[]
getcmds["getGroupPeers"]=[]
getcmds["getNodeIDList"]=[]
getcmds["getGroupList"]=[]
getcmds["getBlockByHash"]=[["str","bool"],"hash : 区块Hash(hash string),是否查询交易数据(true/false for with transaction data)"]
getcmds["getBlockByNumber"]=[["hex","bool"],"number bool : 区块高度(number),是否查询交易数据(true/false for with transaction data)"]
getcmds["getBlockHashByNumber"]=[["hex"],"number : 区块高度(number)"]
getcmds["getTransactionByHash"]=[["str"],"hash : 交易Hash(hash string)"]
getcmds["getTransactionByBlockHashAndIndex"]=[["str","hex"],"blockhash index : 区块Hash(hash string), 交易在区块里的位置(index)"]
getcmds["getTransactionByBlockNumberAndIndex"]=[["hex","hex"],"blocknumber index : 区块高度(number),交易在区块里的位置(index)"]
getcmds["getTransactionReceipt"]=[["str"],"hash: 交易hash(hash string)"]
getcmds["getPendingTransactions"]=[]
getcmds["getPendingTxSize"]=[]
getcmds["getCode"]=["str"]
getcmds["getTotalTransactionCount"]=[]
getcmds["getSystemConfigByKey"]=[["str"],"name : 配置参数名(system param name),eg:tx_count_limit"]

#--------------------------------------------------------------------------------------------
# console cmd entity
#--------------------------------------------------------------------------------------------
usagemsg.append('''all the 'get' command for JSON RPC
各种get接口，查询节点的各种状态（不一一列出，可用list指令查看接口列表和参数名）
neg: [getBlockByNumber 10 true]. 
use 'python console.py list' to show all get cmds ''')
if cmd in getcmds:
    types=[]
    if len(getcmds[cmd]) > 0:
        types = getcmds[cmd][0]
    if "getBlockBy" in cmd:
        #make a default for getBlockBy...
        if(len(inputparams) == 1):
            inputparams.append("false")
            print("**for getBlockbyNumber/Hash , missing 2nd arg ,defaut (false) gave : withoud retrieve transactions detail.full command,eg: getBlockByNumber 10 true (or false)\n")
    try:
        fmtargs = format_args_by_types(inputparams, types)
    except Exception as e:
        cmdinfo = getcmds[cmd]
        memo=" no args"
        if(len(cmdinfo)==2):
            memo =" {} ".format(cmdinfo[1])
        print("args not match,should be : {} {},break\n".format(cmd,memo) )
        sys.exit("please try again...")
    print("is a get :{},params:{}".format(cmd,fmtargs) )
    params = [client.groupid]
    params.extend(fmtargs)
    #print(params)
    sendcmd = cmd
    if cmd=="getNodeVersion": #getNodeVersion is a alias for getClientVersion
        sendcmd = "getClientVersion"
    result  = client.common_request(sendcmd,params)
    print(">> get result:",json.dumps(result,indent=4))

    if cmd == "getTransactionReceipt":
        if len(inputparams) == 2:
            contractname = inputparams[1]
            print_receipt_logs_and_txoutput(result,contractname)

    if cmd == "getBlockNumber":
        print("blocknumber is {}".format(int(result,16)))

    if "getBlockBy" in cmd:
        blocknum = int(result["number"],16)
        print(">> blocknumber : ",blocknum)
        print(">> blockhash   : ", result["hash"])
    if "getTransactionBy" in cmd :
        #print(inputparams)
        abifile=None
        if len(inputparams) == 3:
            abifile = inputparams[2]
        if len(inputparams) == 2 and cmd == "getTransactionByHash":
            abifile = inputparams[1]
        if abifile!=None:
            print_parse_transaction(result,abifile)


#--------------------------------------------------------------------------------------------
# console cmd entity
#--------------------------------------------------------------------------------------------
validcmds.append("list")
usagemsg.append('''list
列出所有支持的get接口名和参数
list: list all  getcmds  has implemented (getBlock...getTransaction...getReceipt..getOthers)''')
if cmd == "list":
    i = 0
    print("query commands:")
    for cmd in getcmds:
        hint = "无参数(no args)"
        if len(getcmds[cmd])==2:
            hint = getcmds[cmd][1]
        i=i+1
        print ("{} ): {}\t{}".format(i,cmd,hint))
        print("----------------------------------------------------------------------------------------")

#--------------------------------------------------------------------------------------------
# console cmd entity
#--------------------------------------------------------------------------------------------
validcmds.append("int")
usagemsg.append('''int [hex number]
输入一个十六进制的数字，转为十进制（考虑到json接口里很多数字都是十六进制的，所以提供这个功能）
convert a hex str to int ,eg: int 0x65''')
if cmd == 'int':
    print(int(inputparams[0],16))

#--------------------------------------------------------------------------------------------
# console cmd entity
#--------------------------------------------------------------------------------------------
validcmds.append("txinput")
usagemsg.append('''txinput [contractname] [inputdata(in hex string)]
复制一段来自transaction的inputdata(十六进制字符串)，指定合约名，则可以自动解析（合约的abi文件应存在指定目录下）
parse the transaction input data by  contractname，eg: txinput SimpleInfo [txinputdata]''')
if cmd =="txinput":
    contractname = inputparams[0]
    inputdata = inputparams[1]
    dataParser = DatatypeParser(default_abi_file(contractname) )
    #print(dataParser.func_abi_map_by_selector)
    result = dataParser.parse_transaction_input(inputdata)
    print("\nabifile : ",default_abi_file(contractname))
    print("parse result: {}".format(result))

#--------------------------------------------------------------------------------------------
# console cmd entity
#--------------------------------------------------------------------------------------------
validcmds.append("checkaddr")
usagemsg.append('''checkaddr [address]
将普通地址转为自校验地址,自校验地址使用时不容易出错
change address to checksum address according EIP55:
to_checksum_address: 0xf2c07c98a6829ae61f3cb40c69f6b2f035dd63fc -> 0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC
''')
if cmd == "checkaddr":
    address = inputparams[0]
    result = to_checksum_address(address)
    print("to_checksum_address:")
    print("{} -->\n{}".format(address,result) )

#--------------------------------------------------------------------------------------------
# console cmd entity
#--------------------------------------------------------------------------------------------
def printusage():
    index = 0
    for msg in usagemsg:
        index+=1
        print("{}): {}\n".format(index,msg) )

validcmds.append("usage")
if cmd == "usage":
    print('''usage
使用说明,输入python console.py [指令 参数列表]
Usage of console (FISCO BCOS 2.0 lite client @python):
python console.py [cmd args]
''')
    printusage()


#--------------------------------------------------------------------------------------------
# console cmd entity
#--------------------------------------------------------------------------------------------
if (cmd not in validcmds) and  (cmd not in getcmds):
    printusage()
    print("console cmd  [{}]  not implement yet,see the usage\n".format(cmd))