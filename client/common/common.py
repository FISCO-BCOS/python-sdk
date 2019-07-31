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
import subprocess
from client_config import client_config
from client.bcoserror import ArgumentsError


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


def execute_cmd(cmd):
    """
    execute command
    """
    data = subprocess.check_output(cmd.split(), shell=False, universal_newlines=True)
    status = 0
    return (status, data)


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
