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
  @function:
  @author: kentzhang
  @date: 2020-10
'''
from client.bcoserror import (
    BcosException,
)
from client.common import common
from console_utils.console_common import *


class CmdAccount:
    client = None
    @staticmethod
    def make_usage():
        usagemsg = []
        usagemsg.append(
            """
>> newaccount [name] [password]
创建一个新帐户，参数为帐户名(如alice,bob)和密码
结果加密保存在配置文件指定的帐户目录 *如同目录下已经有同名帐户文件，旧文件会复制一个备份

>> showaccount [name] [password]
指定帐户名字(不带后缀)和密码，打开配置文件里默认账户文件路径下的对应keystore或json文件，打印公私钥和地址

>> listaccount
列出已经配置的目录下有多少个账户文件。后缀名为'.keystore'为ECDSA密钥，后缀名'.json'为国密文件
【后续再支持更多文件格式如pem,p12等】
""")
        return usagemsg

    def create_gm_account(self, name, password):
        keyfile = "{}/{}.json".format(client_config.account_keyfile_path, name)
        if not os.path.exists(keyfile):  # 如果默认文件不存在，直接写
            forcewrite = True
        else:
            forcewrite = common.backup_file(keyfile)  # 如果备份失败，不要覆盖写

        account = GM_Account()
        account.create()
        if forcewrite:
            account.save_to_file(keyfile, password)
        print("account created:")
        print(account.getdetail())
        if forcewrite:
            print("account save to :", keyfile)

    def create_ecdsa_account(self, name, password):
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
        if not os.access(keyfile, os.F_OK):  # 默认的账号文件不存在，就强行存一个
            forcewrite = True
        else:
            # old file exist,move to backup file first
            forcewrite = common.backup_file(keyfile)  # 如果备份文件不成功，就不要覆盖写了
        if forcewrite:
            with open(keyfile, "w") as dump_f:
                json.dump(kf, dump_f)
                dump_f.close()
        print(">>-------------------------------------------------------")
        print(
            "INFO >> read [{}] again after new account,address & keys in file:".format(
                keyfile
            )
        )
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

    @staticmethod
    def usage():
        msg = CmdAccount.make_usage()
        for m in msg:
            print(m)

    def newaccount(self, inputparams):
        name = inputparams[0]
        max_account_len = 240
        if len(name) > max_account_len:
            common.print_info(
                "WARNING",
                "account name should no more than {}".format(max_account_len),
            )
            sys.exit(1)
        password = inputparams[1]
        forcewrite = False
        if len(inputparams) == 3 and inputparams[2] == "save":
            forcewrite = True
        print("starting : {} {}  , if save:{}".format(name, password, forcewrite))
        if client_config.crypto_type == CRYPTO_TYPE_GM:
            self.create_gm_account(name, password)
        else:
            self.create_ecdsa_account(name, password)

    def show_gm_account(self, name, password):

        account = GM_Account()
        keyfile = "{}/{}.json".format(client_config.account_keyfile_path, name)
        account.load_from_file(keyfile, password)
        print("load account from file: ", keyfile)
        print(account.getdetail())

    def show_ecdsa_account(self, name, password):

        keyfile = "{}/{}.keystore".format(client_config.account_keyfile_path, name)
        # the account doesn't exists
        if os.path.exists(keyfile) is False:
            raise BcosException("account {} doesn't exists".format(name))
        print(
            "show account : {}, keyfile:{} ,password {}  ".format(
                name, keyfile, password
            )
        )
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
            raise BcosException(
                ("load account info for [{}] failed," " error info: {}!").format(
                    name, e
                )
            )

    def listaccount(self, inputparams):
        accountlist = list_files("bin/accounts/*.keystore")
        for name in accountlist:
            print(name)
        accountlist = list_files("bin/accounts/*.json")
        for name in accountlist:
            print(name)

    def showaccount(self, inputparams):
        name = inputparams[0]
        password = inputparams[1]
        if client_config.crypto_type == CRYPTO_TYPE_GM:
            self.show_gm_account(name, password)
        else:
            self.show_ecdsa_account(name, password)


if False:

    cname = "cmd_account"
    #obj = getClassbyName(cname)
    #obj =globals()[cname]
    #console_run(cname, ["create", "tester", "123456"])
    #console_run(obj, ["list"])
    #console_run(obj, ["usage"])
    console_run_byname("cmd_account", "list")
    #console_run(acc, ["show", "pyaccount", "123456"])
    #(code, msg) = console_run(acc,["noway"])
    # for m in msg:
    #   print(m)
