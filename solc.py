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
  @author: kentzhang
  @date: 2019-07
  ** Read bin/solc/README.md , to download solc binary release first
  use solc binary to compile solidity contract.output abi & bin files.
'''
import os
import sys
solc_bin = "bin/solc/solc"
solc_option = "--abi --bin --overwrite"
solc_default_output = "./contracts"


# sample:
# bin/solc/solc.exe --abi --bin --allow-paths=./contracts
# contracts/AddressTableWorker.sol -o ./tmp
def sol_cmdline(solfile, outputpath, option=solc_option):
    solpath = os.path.dirname(solfile)
    allowpath = ""
    if(len(solpath) > 0):
        allowpath = "--allow-paths=" + solpath
    cmdline = "{} {} {} -o {} {}".format(solc_bin, option, allowpath, outputpath, solfile)
    return cmdline


def run_cmd(cmdline):
    res = os.popen(cmdline).readlines()
    return res


def run_solc(solfile, outputpath, option=solc_option):
    cmdline = sol_cmdline(solfile, outputpath, option)
    print(cmdline)
    res = run_cmd(cmdline)
    if len(res) > 0:
        print(res)


if __name__ == '__main__':
    # print (sys.argv)
    if(len(sys.argv) == 1):
        print("\nusage: python solc.py [contract file (with path)] [output dir]\n")
        print("** Read bin/solc/README.md , to download solc binary release first **")
        sys.exit(0)
    solfile = sys.argv[1]
    outputdir = solc_default_output
    if (len(sys.argv) == 3):
        outputdir = sys.argv[2]
    print("compile [{}],output to [{}]".format(solfile, outputdir))
    run_solc(solfile, outputdir)
    print("** please check the output dir ->[ {} ]".format(outputdir))
