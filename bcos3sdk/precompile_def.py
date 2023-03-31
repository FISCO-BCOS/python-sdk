from client.datatype_parser import DatatypeParser

SYS_CONFIG_PRECOMPILED_ADDRESS =  "0000000000000000000000000000000000001000"
TABLE_MANAGER_PRECOMPILED_ADDRESS =   "0000000000000000000000000000000000001002"

CONSENSUS_PRECOMPILED_ADDRESS =   "0000000000000000000000000000000000001003"

CONTRACT_AUTH_ADDRESS = "0000000000000000000000000000000000001005"

BFS_PRECOMPILED_ADDRESS = "000000000000000000000000000000000000100e"

COMMITTEE_MANAGER_ADDRESS =      "0000000000000000000000000000000000010001"

ACCOUNT_MANAGER_ADDRESS = "0000000000000000000000000000000000010003"

PRECOMPILED_SOL_PATH = "bcos3sdk/sol"
PRECOMPILED_ABI_PATH = f"{PRECOMPILED_SOL_PATH}/abi"


class PrecompileHelper:
    
    address = ""
    abi_file = ""
    abi_parser = None
    
    def __init__(self,filename:str,address):
        self.address = address
        if not filename.endswith(".abi"):
            filename = filename + ".abi"
        abipath = PRECOMPILED_ABI_PATH
        self.abi_file = f"{abipath}/{filename}"
        self.abi_parser = DatatypeParser(self.abi_file)
    
