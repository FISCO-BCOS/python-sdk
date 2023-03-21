#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-
"""
  FISCO BCOS/Python-SDK is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/)
  FISCO BCOS/Python-SDK is free software: you can redistribute it and/or modify it under the
  terms of the MIT License as published by the Free Software Foundation. This project is
  distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Thanks for
  authors and contributors of eth-abi, eth-account, eth-hash，eth-keys, eth-typing, eth-utils,
  rlp, eth-rlp , hexbytes ... and relative projects
  @author: kentzhang
  @date: 2019-06

"""
hint = '''
python sdk 适配FISCO BCOS 2.x/3.x版本，控制台的实现文件做了分离。

README文档的命令行示例里未做版本区分，仅供演示参考，实际使用时：

* 如面向FISCO BCOS2.x，把console.py换成console2.py。如: python console2.py getBlockNumber

* 如面向FISCO BCOS3.x，把console.py换成console3.py。如: python console3.py getBlockNumber

demo目录里的demo_get2/3, demo_transaction2/3的逻辑与此类似。

'''

print(hint)