from client.bcosclient import BcosClient
import os
from client.stattool import StatTool
from client.datatype_parser import DatatypeParser
from client.common.compiler import Compiler
from client_config import client_config
from client.bcoserror import BcosException, BcosError
from client.contractnote import ContractNote
from eth_utils import encode_hex,decode_hex
import uuid
from eth_utils.crypto import  keccak
import json
# 从文件加载abi定义
abi_file = "contracts/HelloEvent.abi"
parser = data_parser = DatatypeParser(abi_file)
contract_abi = data_parser.contract_abi
contractnode = ContractNote()
address = contractnode.get_last("HelloEvent")
print("event contract address is ",address)
client  = None
client = BcosClient()
info = client.getinfo()
print("client info:", info)
params_set = ["aaabbb"]
params_setnum_5 = ["setnum_ab",5]
params_setnum_10 = ["setnum_ab",10]
params_settwo_1 = ["settwo_aabb",10,'key1']
params_settwo_2 = ["settwo_aabb",10,'key2']


def format_event_register_request(from_block,to_block,addresses,topics,groupid = "1",filterid= None):
    '''
    {
  "fromBlock": "latest",
  "toBlock": "latest",
  "addresses": [
    0xca5ed56862869c25da0bdf186e634aac6c6361ee
  ],
  "topics": [
    "0x91c95f04198617c60eaf2180fbca88fc192db379657df0e412a9f7dd4ebbe95d"
  ],
  "groupID": "1",
  "filterID": "bb31e4ec086c48e18f21cb994e2e5967"
}'''
    request = dict()
    request["fromBlock"] = from_block
    request["toBlock"] = to_block
    request["addresses"] = addresses
    request["topics"] = topics
    request["groupID"] = groupid
    if filterid == None:
        #generate an id in uuid
        seq = uuid.uuid1()
        #seq32 = "".join(str(seq).split("-")).upper()
       # seq32bytes = bytes(seq32, encoding='utf-8')
        #sha_seq =  keccak(bytes(seq32bytes))
        filterid = seq.hex
    request["filterID"] = filterid
   # print(json.dumps(request,indent=4))
    return request


'''
    CHANNEL_RPC_REQUEST = 0x12,        // type for rpc request
    CLIENT_HEARTBEAT = 0x13,           // type for heart beat for sdk
    CLIENT_HANDSHAKE = 0x14,           // type for hand shake
    CLIENT_REGISTER_EVENT_LOG = 0x15,  // type for event log filter register request and response
    AMOP_REQUEST = 0x30,               // type for request from sdk
    AMOP_RESPONSE = 0x31,              // type for response to sdk
    AMOP_CLIENT_TOPICS = 0x32,         // type for topic request
    AMOP_MULBROADCAST = 0x35,          // type for mult broadcast
    REQUEST_TOPICCERT = 0x37,          // type request verify
    UPDATE_TOPIICSTATUS = 0x38,        // type for update status
    TRANSACTION_NOTIFY = 0x1000,       // type for  transaction notify
    BLOCK_NOTIFY = 0x1001,             // type for  block notify
    EVENT_LOG_PUSH = 0x1002            // type for event log push
'''
CLIENT_REGISTER_EVENT_LOG = 0x15 # type for event log filter register request and response
REQUEST_TOPICCERT = 0x37 # type request verify

def test_register_event():
    topic = parser.topic_from_event_name("onset")
    requestdata = format_event_register_request("lastest", "lastest", address, [topic])
    print("register event: ",requestdata)
    result =  client.channel_handler.make_channel_request(requestdata,CLIENT_REGISTER_EVENT_LOG,REQUEST_TOPICCERT)
    print("after register:")
    print(result)

def test_event():
    receipt = client.rpc_sendRawTransactionGetReceipt(address,contract_abi,"set",params_set)
    print(json.dumps(receipt,indent=4) )
    logresult = parser.parse_event_logs(receipt["logs"])
    i = 0
    #print(json.dumps(logresult,indent=4))
    for log in logresult:
        if 'eventname' in log:
            i = i + 1
            print("{}): log name: {} , data: {} , topic: {}".format(i, log['eventname'], log['eventdata'],log['topic']))
    txhash = receipt["transactionHash"]
    assert 1==1

topic = parser.topic_from_event_name("onset")
format_event_register_request("lastest","lastest",address,[topic])
#test_event()
test_register_event()
import time
time.sleep(5)
client.finish()