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
  @file: consensus_precompile.py
  @function:
  @author: yujiechen
  @date: 2019-07
'''
import os
import subprocess
from client.common import common
from client_config import client_config
from client.bcoserror import CompilerNotFound, CompileError
from eth_utils.crypto import CRYPTO_TYPE_GM, CRYPTO_TYPE_ECDSA


class Compiler:
    """
    compile sol into bin and abi
    """
    _env_key_ = "SOLC_BINARY"
    if client_config.crypto_type == CRYPTO_TYPE_ECDSA:
        compiler_path = client_config.solc_path
    elif client_config.crypto_type == CRYPTO_TYPE_GM:
        compiler_path = client_config.gm_solc_path
    else:
        raise CompileError("crypto_type: {} is not supported".format(client_config.crypto_type))

    @staticmethod
    def compile_with_solc(sol_file, contract_name, output_path):
        """
        compile with solc
        """
        # sol_file
        command = "{} --bin --abi {} -o {} --overwrite".format(
            Compiler.compiler_path, sol_file, output_path)
        print("INFO >> compile with solc compiler : ", command)
        common.execute_cmd(command)

    @staticmethod
    def compile_file(sol_file, output_path="contracts"):
        """
        get abi and bin
        """
        # get contract name
        contract_name = os.path.basename(sol_file).split('.')[0]
        try:
            # compiler not found
            if os.path.isfile(Compiler.compiler_path) is False and \
                    os.path.isfile(Compiler.js_compiler_path) is False:
                raise CompilerNotFound(("solc compiler: {} and solcjs compiler {}"
                                        " both doesn't exist,"
                                        " please install firstly !").
                                       format(Compiler.compiler_path,
                                              Compiler.js_compiler_path))
            # compile with solc if solc compiler exists
            if os.path.isfile(Compiler.compiler_path) is True:
                Compiler.compile_with_solc(sol_file, contract_name, output_path)
        except CompilerNotFound as e:
            abi_path = output_path + "/" + contract_name + ".abi"
            bin_path = output_path + "/" + contract_name + ".bin"
            # exist abi
            if os.path.exists(abi_path) is False or os.path.exists(bin_path) is True:
                raise CompileError(("compile failed ! both the compiler not"
                                    " found and the bin/abi"
                                    " not found, error information: {}").format(e))
        except subprocess.CalledProcessError as e:
            raise CompileError("compile error for compile failed, error information: {}".format(e))
        except Exception as e:
            raise CompileError("compile {} failed, error information: {}".format(sol_file, e))
