from bcos3sdk.bcos3client import Bcos3Client
from bcos3sdk.precompile_def import CONSENSUS_PRECOMPILED_ADDRESS, PrecompileHelper

warning = "!!WARNING:节点的操作对链共识出块影响极大，一般不建议在客户端调用!" \
          "建议在WeBASE,控制台等有权限控制、网络安全保障的系统上对sealer进行操作"
class ConsensusPrecompile:
    name = "ConsensusPrecompiled"
    address = CONSENSUS_PRECOMPILED_ADDRESS
    helper = PrecompileHelper(name,address)
    
    def __init__(self,client:Bcos3Client):
        self.client = client;

    
    def addSealer(self, nodeId, weight):
        print(warning)
        abi_parser = self.helper.abi_parser
        params = [nodeId, weight]
        method_name = "addSealer"
        response = self.client.sendRawTransaction(CONSENSUS_PRECOMPILED_ADDRESS,
                                           abi_parser.contract_abi,
                                           method_name,
                                           params)
    
        if ("output" in response):
            output = abi_parser.parse_output(method_name, response["output"])
            response["outputs"] = output
        
        return response

    
    def addObserver(self, nodeId):
        print(warning)
        abi_parser = self.helper.abi_parser
        params = [nodeId]
        method_name = "addObserver"
        response = self.client.sendRawTransaction(CONSENSUS_PRECOMPILED_ADDRESS,
                                           abi_parser.contract_abi,
                                           method_name,
                                           params)
        if ("output" in response):
            output = abi_parser.parse_output(method_name, response["output"])
            response["outputs"] = output
        
        return response

    
    def removeNode(self, nodeId):
        print(warning)
        abi_parser = self.helper.abi_parser
        params = [nodeId]
        method_name = "remove"
        response = self.client.sendRawTransaction(CONSENSUS_PRECOMPILED_ADDRESS,
                                           abi_parser.contract_abi,
                                           method_name,
                                           params)
        if ("output" in response):
            output = abi_parser.parse_output(method_name, response["output"])
            response["outputs"] = output
        
        return response

    
    def setWeight(self, nodeId, weight):
        print(warning)
        abi_parser = self.helper.abi_parser
        params = [nodeId, weight]
    
        method_name = "setWeight"
        response = self.client.sendRawTransaction(CONSENSUS_PRECOMPILED_ADDRESS,
                                           abi_parser.contract_abi,
                                           method_name,
                                           params)
        if ("output" in response):
            output = abi_parser.parse_output(method_name, response["output"])
            response["outputs"] = output
        
        return response

