#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
  FISCO BCOS/Python-SDK is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/)
  FISCO BCOS/Python-SDK is free software: you can redistribute it and/or modify it under the
  terms of the MIT License as published by the Free Software Foundation. This project is
  distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Thanks for
  authors and contributors of eth-abi, eth-account, eth-hash，eth-keys, eth-typing, eth-utils,
  rlp, eth-rlp , hexbytes ... and relative projects
  @author: kentzhang
  @date: 2020-01
'''

from client.gm_account import GM_Account
from collections import (
    Mapping,
)

from gmssl import sm2, func
from gmssl import sm2_helper
from eth_utils.crypto import CRYPTO_TYPE_GM, CRYPTO_TYPE_ECDSA

from eth_account.datastructures import (
    AttributeDict,
)

from cytoolz import (
    dissoc,
)

from eth_utils.hexadecimal import encode_hex, decode_hex
from client.bcostransactions import (
    ChainAwareUnsignedTransaction,
    BcosUnsignedTransaction,
    encode_transaction,
    serializable_unsigned_transaction_from_dict,
    strip_signature,
)

from eth_utils.curried import (
    combomethod,
    hexstr_if_str,
    is_dict,
    keccak,
    text_if_str,
    to_bytes,
    to_int,
)
from hexbytes import (
    HexBytes,
)
from client.bcoskeypair import BcosKeyPair
from client.bcoserror import BcosException
from eth_account.signers.local import (
    LocalAccount,
)

CHAIN_ID_OFFSET = 35
V_OFFSET = 27

# signature versions
PERSONAL_SIGN_VERSION = b'E'  # Hex value 0x45
INTENDED_VALIDATOR_SIGN_VERSION = b'\x00'  # Hex value 0x00
STRUCTURED_DATA_SIGN_VERSION = b'\x01'  # Hex value 0x01


class SignTx():
    gm_account = None  # 国密的账号
    ecdsa_account = None  # ECDSA的公私钥对象，类型为 LocalAccount : eth_account/signers/local.py
    crypto_type = None  # 加密类型，国密或通用，来自eth_utils/crypto.py的CRYPTO_TYPE_GM，CRYPTO_TYPE_ECDSA

    def to_eth_v(self, v_raw, chain_id=None):
        if chain_id is None:
            v = v_raw + V_OFFSET
        else:
            v = v_raw + CHAIN_ID_OFFSET + 2 * chain_id
        return v

    def sign_transaction_hash(self, transaction_hash, chain_id):
        hashbyte = bytes(transaction_hash)
        if self.crypto_type == CRYPTO_TYPE_GM:
            # gm sign
            public_key = self.gm_account.keypair.public_key
            private_key = self.gm_account.keypair.private_key
            sm2_crypt = sm2.CryptSM2(
                public_key=public_key, private_key=private_key)
            public_key = self.gm_account.keypair.public_key
            private_key = self.gm_account.keypair.private_key
            (r, s) = sm2_crypt.sign(hashbyte)
            v_raw = public_key
            v = int(v_raw, 16)
        elif self.crypto_type == CRYPTO_TYPE_ECDSA:
            # ecdsa sign
            signature = self.ecdsa_account._key_obj.sign_msg_hash(transaction_hash)
            (v_raw, r, s) = signature.vrs
            v = self.to_eth_v(v_raw, chain_id)
        else:
            raise BcosException(
                "when sign transaction, unknown crypto type {}".format(
                    self.crypto_type))

        return (v, r, s)
    '''
        debug = False
        if debug: #debug gm
            print("transaction_hash in hex", encode_hex(transaction_hash))
            print("transaction_hash in byte:", hashbyte)
            print(len(hashbyte))
            signstr = sm2_crypt.combine_signed_R_S(r, s)
            data = transaction_hash
            verify = sm2_crypt.verify(signstr, data)
            print('verify:%s' % verify)
            print("privatekey: ", private_key)
            print("data to sign:", transaction_hash)
            print("SIGN to V:%s,len:%d" % (v_raw, len(v_raw)))
            print("SIGN to R:", r)  # guomi
            print("SIGN to R(hex): %064x" % (r))  # guomi
            print("SIGN to S(hex): %064x" % (s))
            print('signstr:%s' % signstr)
            print(v)
            print("hex_v:", hex(v))
       '''

    def sign_transaction_dict(self, transaction_dict):
        # generate RLP-serializable transaction, with defaults filled
        unsigned_transaction = serializable_unsigned_transaction_from_dict(transaction_dict)

        transaction_hash = unsigned_transaction.hash()

        # detect chain
        if isinstance(unsigned_transaction, BcosUnsignedTransaction):
            chain_id = None
        else:
            chain_id = unsigned_transaction.v

        # sign with private key
        (v, r, s) = self.sign_transaction_hash(transaction_hash, chain_id)

        # serialize transaction with rlp
        encoded_transaction = encode_transaction(unsigned_transaction, vrs=(v, r, s))

        return (v, r, s, encoded_transaction)

    def sign_transaction(self, transaction_dict):

        if not isinstance(transaction_dict, Mapping):
            raise TypeError("transaction_dict must be dict-like, got %r" % transaction_dict)

        # allow from field, *only* if it matches the private key
        if 'from' in transaction_dict:
            if transaction_dict['from'] == self.KeyPair.address:
                sanitized_transaction = dissoc(transaction_dict, 'from')
            else:
                raise TypeError("from field must match key's %s, but it was %s" % (
                    self.KeyPair.address,
                    transaction_dict['from'],
                ))
        else:
            sanitized_transaction = transaction_dict

        # sign transaction
        (
            v,
            r,
            s,
            rlp_encoded,
        ) = self.sign_transaction_dict(sanitized_transaction)

        transaction_hash = keccak(rlp_encoded)

        return AttributeDict({
            'rawTransaction': HexBytes(rlp_encoded),
            'hash': HexBytes(transaction_hash),
            'r': r,
            's': s,
            'v': v,
        })
