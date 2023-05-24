#cyber2023.03 by kent
class TransactionStatus:
    OK = "0"
    Unknown = "1"
    OutOfGasLimit = "2"  # Too little gas to pay for the base transaction cost.
    NotEnoughCash = "7"  # TODO: remove this?
    BadInstruction = "10"
    BadJumpDestination = "11"
    OutOfGas = "12"  # Ran out of gas executing code of the transaction.
    OutOfStack = "13"  # Ran out of stack executing code of the transaction.
    StackUnderflow = "14"
    PrecompiledError = "15"
    RevertInstruction = "16"
    ContractAddressAlreadyUsed = "17"
    PermissionDenied = "18"
    CallAddressError = "19"
    GasOverflow = "20"
    ContractFrozen = "21"
    AccountFrozen = "22"
    AccountAbolished = "23"
    ContractAbolished = "24"
    WASMValidationFailure = "32"
    WASMArgumentOutOfRange = "33"
    WASMUnreachableInstruction = "34"
    WASMTrap = "35"
    NonceCheckFail = "10000"  # txPool related errors
    BlockLimitCheckFail = "10001"
    TxPoolIsFull = "10002"
    Malform = "10003"
    AlreadyInTxPool = "10004"
    TxAlreadyInChain = "10005"
    InvalidChainId = "10006"
    InvalidGroupId = "10007"
    InvalidSignature = "10008"
    RequestNotBelongToTheGroup = "10009"
    TransactionPoolTimeout = "10010"

    @staticmethod
    def get_error_message(error_code):
        error_dict = {
            "0": "OK",
            "1": "Unknown",
            "2": "OutOfGasLimit",
            "7": "NotEnoughCash",
            "10": "BadInstruction",
            "11": "BadJumpDestination",
            "12": "OutOfGas",
            "13": "OutOfStack",
            "14": "StackUnderflow",
            "15": "PrecompiledError",
            "16": "RevertInstruction",
            "17": "ContractAddressAlreadyUsed",
            "18": "PermissionDenied",
            "19": "CallAddressError",
            "20": "GasOverflow",
            "21": "ContractFrozen",
            "22": "AccountFrozen",
            "23": "AccountAbolished",
            "24": "ContractAbolished",
            "32": "WASMValidationFailure",
            "33": "WASMArgumentOutOfRange",
            "34": "WASMUnreachableInstruction",
            "35": "WASMTrap",
            "10000": "NonceCheckFail",
            "10001": "BlockLimitCheckFail",
            "10002": "TxPoolIsFull",
            "10003": "Malform",
            "10004": "AlreadyInTxPool",
            "10005": "TxAlreadyInChain",
            "10006": "InvalidChainId",
            "10007": "InvalidGroupId",
            "10008": "InvalidSignature",
            "10009": "RequestNotBelongToTheGroup",
            "10010": "TransactionPoolTimeout"
        }
        error_code = TransactionStatus.convert_error_code(error_code)
        return error_dict.get(error_code, "Unknown error code")


    @staticmethod
    def convert_error_code(error_code):
        if isinstance(error_code, int):
            error_code = str(error_code)
        return error_code
    
    @staticmethod
    def isOK(input):
        if str(input) == TransactionStatus.OK:
            return True
        else:
            return False
