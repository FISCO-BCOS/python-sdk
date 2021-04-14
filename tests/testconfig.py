'''
  @author: kentzhang
  @date: 2019-06
'''
import os
from configobj import ConfigObj

fname = "hello.wasm"
print(os.path.splitext(fname))
fname = "hello"
print(os.path.splitext(fname))

config = ConfigObj("sample/contract.ini", encoding='UTF8')

config['address'] = {}
config['address']['SimpleInfo'] = "0x0b8ae6ce3850cedf8ebf6b6a7b949bb085d3ad17"
config['address']['testnode'] = "this is a test"


# 写入
config.write()
# 读配置文件
print(config['address'])
print(config['address']['SimpleInfo'])
print(config['address']['testnode'])


del config['address']['testnode']
config.write()

