#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
  bcosliteclientpy is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/)
  bcosliteclientpy is free software: you can redistribute it and/or modify it under the
  terms of the MIT License as published by the Free Software Foundation. This project is
  distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Thanks for
  authors and contributors of eth-abi, eth-account, eth-hash，eth-keys, eth-typing, eth-utils,
  rlp, eth-rlp , hexbytes ... and relative projects
  @author: kentzhang
  @date: 2020-01
'''

from collections import (
    Mapping,
)

from gmssl import sm2, func
from gmssl import sm2_helper

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


CHAIN_ID_OFFSET = 35
V_OFFSET = 27

# signature versions
PERSONAL_SIGN_VERSION = b'E'  # Hex value 0x45
INTENDED_VALIDATOR_SIGN_VERSION = b'\x00'  # Hex value 0x00
STRUCTURED_DATA_SIGN_VERSION = b'\x01'  # Hex value 0x01
GM_TYPE='gm'
from client.gm_account import  GM_Account




class SignTx():
    account = GM_Account()


    def sign_transaction_hash(self,transaction_hash, chain_id):
        public_key =self.account.public_key
        private_key = self.account.private_key
        sm2_crypt = sm2.CryptSM2(
            public_key=public_key, private_key=private_key)
        hashbyte= bytes(transaction_hash)
        #transaction_hash =keccak(transaction_hash)
        (r,s) = sm2_crypt.sign(hashbyte)
        v_raw = public_key

        #V = int(v_raw,16) #self.to_eth_v(v_raw, chain_id)
        v= int(v_raw,16)
        debug =False
        if debug:
            print("transaction_hash in hex",encode_hex(transaction_hash))
            print("transaction_hash in byte:",hashbyte)
            print(len(hashbyte))
            signstr = sm2_crypt.combine_signed_R_S(r, s)
            data = transaction_hash
            verify = sm2_crypt.verify(signstr, data)
            print('verify:%s' % verify)
            print("privatekey: ",private_key)
            print("data to sign:",transaction_hash)
            print("SIGN to V:%s,len:%d"%(v_raw,len(v_raw)) )
            print("SIGN to R:",r) #guomi
            print("SIGN to R(hex): %064x"%(r))  # guomi
            print("SIGN to S(hex): %064x"%(s))
            print('signstr:%s' % signstr)
            print(v)
            print("hex_v:",hex(v))
        return (v,r,s)

    def sign_transaction_dict(self,transaction_dict):
        # generate RLP-serializable transaction, with defaults filled
        unsigned_transaction = serializable_unsigned_transaction_from_dict(transaction_dict)

        transaction_hash = unsigned_transaction.hash()

        #print("transaction_hash",encode_hex(transaction_hash) )
        #print("transaction_hash len",len(transaction_hash))
        #print(transaction_hash.hex())
        #print(len(transaction_hash.hex()))
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
            if transaction_dict['from'] == self.account.address:
                sanitized_transaction = dissoc(transaction_dict, 'from')
            else:
                raise TypeError("from field must match key's %s, but it was %s" % (
                    self.account.address,
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
