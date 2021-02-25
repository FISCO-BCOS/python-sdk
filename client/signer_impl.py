from client.gm_account import GM_Account
from eth_account.signers.local import LocalAccount
from gmssl import sm2
from gmssl.sm2 import CryptSM2


class Signer_Impl:
    def sign(self, data_in_byte, chain_id=None):
        pass
    def get_address(self):
        pass

#国密的签名实现
class Signer_GM(Signer_Impl):
    gm_account: GM_Account
    sm2_crypt: CryptSM2

    def __init__(self, account):
        self.gm_account = account

    def get_address(self):
        return self.gm_account.keypair.address

    def sign(self, data_in_byte, chain_id=None):
        if self.sm2_crypt is None:
            self.sm2_crypt = sm2.CryptSM2(
                public_key=self.gm_account.keypair.public_key,
                private_key=self.gm_account.keypair.private_key)
        (r, s) = self.sm2_crypt.sign(data_in_byte)
        v_raw = self.publickey
        v = int(v_raw, 16)
        return (v, r, s)




#ecdsa的签名实现
class Signer_ECDSA(Signer_Impl):
    CHAIN_ID_OFFSET = 35
    V_OFFSET = 27
    # signature versions
    PERSONAL_SIGN_VERSION = b'E'  # Hex value 0x45
    INTENDED_VALIDATOR_SIGN_VERSION = b'\x00'  # Hex value 0x00
    STRUCTURED_DATA_SIGN_VERSION = b'\x01'  # Hex value 0x01

    ecdsa_account: LocalAccount

    def __init__(self, account):
        self.ecdsa_account = account

    def to_eth_v(self, v_raw, chain_id=None):
        if chain_id is None:
            v = v_raw + Signer_ECDSA.V_OFFSET
        else:
            v = v_raw + Signer_ECDSA.CHAIN_ID_OFFSET + 2 * chain_id
        return v

    def get_address(self):
        return self.ecdsa_account.address

    def sign(self, data_in_byte, chain_id=None):
        #print("ecdsa_account:",self.ecdsa_account)
        signature = self.ecdsa_account._key_obj.sign_msg_hash(data_in_byte)
        (v_raw, r, s) = signature.vrs
        v = self.to_eth_v(v_raw, chain_id)
        return (v, r, s)
