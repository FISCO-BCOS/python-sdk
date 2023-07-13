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
bindata = "0x6d4ce63c"



bcos3client = Bcos3Client()
cbfuture = BcosCallbackFuture(sys._getframe().f_code.co_name, "")
group="group0";
node="";
to_address = "0xbe6e9bef148d9c3ac77f28c426e609ea7b7e437a";

bcos3client.bcossdk.bcos_rpc_call(bcos3client.bcossdk.sdk, s2b(group), s2b(node),s2b(to_address),
                                               s2b(bindata),
                                               #signedtx,
                                               cbfuture.callback, byref(cbfuture.context))
(is_timeout,resp) = cbfuture.wait();
print("resp: ",resp)
result = bcos3client.get_result(resp.data);
print("result",result);

