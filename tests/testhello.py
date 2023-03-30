addr = '0xceaf70129ce627a825b2c0ad60402b72a5a359ef'

import sys
sys.path.append("./")
from client.bcosclient import BcosClient

client = BcosClient()
crtAddr = "0xceaf70129ce627a825b2c0ad60402b72a5a359ef"
abi = [{"inputs":[],"name":"getMsg","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"_m","type":"string"}],"name":"setMsg","outputs":[],"stateMutability":"nonpayable","type":"function"}]
print(abi)

abi1 = [{'inputs': [], 'name': 'getMsg', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'string', 'name': '_m', 'type': 'string'}], 'name': 'setMsg', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}]
data = client.call(crtAddr,abi1,"getMsg")
print(data)
#data = client.sendRawTransactionGetReceipt(crtAddr,helloabi,"setMsg",["hello,yekai007!"])
#print(data)
#data = client.call(crtAddr,helloabi,"getMsg")
#print("test:",data)

client.finish()
