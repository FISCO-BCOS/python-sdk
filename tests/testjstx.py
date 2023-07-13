import sys
from ctypes import byref

from bcos3sdk.bcos3callbackfuture import BcosCallbackFuture
from bcos3sdk.bcos3client import Bcos3Client
from bcos3sdk.bcos3datadef import s2b
from client.datatype_parser import DatatypeParser
from client.signer_impl import Signer_ECDSA
from eth_account.account import Account
from eth_keys.backends.native.ecdsa import ecdsa_raw_recover
from eth_utils import decode_hex, keccak, encode_hex
rawTxData = ""
bindata = b''
with open("d:/temp/txdata.txt","rb") as f:
    bindata = f.read()
    f.close()

privkey = "255f01b066a90853a0aa18565653d7b944cd2048c03613a9ff31cb9df9e693e5"
account = Account.privateKeyToAccount(privkey)

with open("d:/temp/tx.txt","r") as f:
    rawTxData = f.read()
    f.close()
rawTxData = '1a10012606636861696e30360667726f757030410e1d5627333031303033303639333538363839333431393837383733373038323036343932343833353834662a3078626536653962656631343864396333616337376632386334323665363039656137623765343337617d0000644ed3885e0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000c74657374383838312d616263000000000000000000000000000000000000000086000b2d000020c9211b6e4b763161b7a75d48dc8480966ad68236d784ac45710d78a3816e24c83d000041db5f257c1db4cc78b4f1407f47a432a9f7f2ee95259ef66b26e97f406ea5ef621c4d01f68d833a28874b0d93fb144f22ddc9cfbed5b6138c5a723bf93687e1b1004c5c7d000c8600';
print(f"rawTxData : (len({len(rawTxData)})):",rawTxData)
bcos3client = Bcos3Client()
cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
group="group0";
node="";


bcos3client.bcossdk.bcos_rpc_send_transaction(bcos3client.bcossdk.sdk, s2b(group), s2b(node),
                                               s2b(rawTxData),
                                               #signedtx,
                                               0, cbfuture.callback, byref(cbfuture.context))
(is_timeout,resp) = cbfuture.wait();
print("tx_resp: ",resp)

result = bcos3client.get_result(resp.data);
print("tx_result: ",result);

to_address = "0xbe6e9bef148d9c3ac77f28c426e609ea7b7e437a";
contractFile = r"contracts\HelloWorld.abi"
abi_parser = DatatypeParser()
abi_parser.load_abi_file(contractFile)
contract_abi = abi_parser.contract_abi
get_result = bcos3client.call(to_address,contract_abi,"get",[])
print("call after set:",get_result)

'''
#检查签名逻辑
signner = Signer_ECDSA.from_privkey(privkey)
(v, r, s) = signner.sign(hash)
print(((v, r, s)))
#v = v-27
from Crypto.Util.number import long_to_bytes
# 将v、r、s转换为字节数组
v_bytes = long_to_bytes(v)
r_bytes = long_to_bytes(r)
s_bytes = long_to_bytes(s)

# 将v、r、s拼接成一个字节数组
signature_bytes = b"".join([ r_bytes, s_bytes,v_bytes])
# 将字节数组转换为字符串
signature_str = signature_bytes.hex()
print("sigv0:",signature_str)
recoverres = ecdsa_raw_recover(hash, (v-27, r, s))
pubkey = encode_hex(recoverres)
print("raw recover result,pubkey:", pubkey)
print("act pubkey = ",signner.keypair.public_key)
'''
