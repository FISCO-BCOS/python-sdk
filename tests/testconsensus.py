import sys
sys.path.append("./")
import json

from bcos3sdk.bcos3client import Bcos3Client
from bcos3sdk.consensus_precompile import ConsensusPrecompile

bcos3client  =Bcos3Client()

client = ConsensusPrecompile(bcos3client)

nodeid = "0384bdf82b9f33a326a9c67c06b4e52f3afee7c596e7bc0b38083eef42e3921c3c7ce1ad2eaa8f8c9cf66a4dfcff3c54d9a443b35cd626a9943ca914c67fe15b"
response = client.setWeight(nodeid,1)

print("response is",json.dumps(response,indent=4))

nodeid = "testid"

response = client.addSealer(nodeid,1)
print("response is",json.dumps(response,indent=4))

response = client.addObserver(nodeid)
print("response is",json.dumps(response,indent=4))


response = client.removeNode(nodeid)
print("response is",json.dumps(response,indent=4))

