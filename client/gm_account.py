#建立一个简单的国密账户类，只管理私钥，和转换到公钥，地址
#可以保存为pem文件，或者从明文文件加载私钥，然后转换
#不做签名，Account应该是签名的一个输入参数
#**原来已经实现的，使用ecdsa的account，暂时不做重构，保持其稳定性
import base64
import binascii
from gmssl import sm2, func
from gmssl import sm2_helper
from gmssl import sm3, func
from eth_utils.hexadecimal import decode_hex,encode_hex
from eth_utils import to_checksum_address
from eth_utils.crypto import  *
from gmssl.sm4 import CryptSM4,SM4_DECRYPT,SM4_ENCRYPT
import json

class GM_Account(object):
    #return keypair ()
    private_key = None
    public_key = None
    address = None
    cbc_iv =  b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    def getdetail(self,sep="\n"):
        str = "private key: %s%spublic key %s%saddress %s"%(self.private_key,sep,self.public_key,sep,self.address)
        return str;

    def publickey_to_address(self,publickey):
        publickeybytes  =func.bytes_to_list(bytes(decode_hex(publickey)) )
        hashres =  sm3.sm3_hash(publickeybytes) #sm3_hash 对应sm3_implement.py里的sm3_hash,返回的是hex形态的结果
        hash_raw = decode_hex(hashres) #转为bytes
        addr_raw = hash_raw[-20:] #截取20个字节
        addr = to_checksum_address(addr_raw) #转为格式化的地址
        return addr

    def create(self):
        kp = sm2_helper.sm2_key_pair_gen()
        self.private_key = kp[0]
        self.public_key = kp[1]
        self.address = self.publickey_to_address(self.public_key)

    def from_key(self,privkey):
        self.public_key = sm2_helper.sm2_privkey_to_pub(privkey)
        self.private_key = privkey
        self.address = self.publickey_to_address(self.public_key)


    def pwd_ljust(self,password):
        return password.ljust(16,'0')


    def save_to_file(self, filename, password = None):
        content = {}
        key = self.private_key
        content["address"] = self.address
        content["encrypt"] = False
        if password is not None and len(password) >0 :
            crypt_sm4 = CryptSM4()
            password = self.pwd_ljust(password)
            crypt_sm4.set_key(bytes(password ,"utf-8"), SM4_ENCRYPT)
            encrypt_value = crypt_sm4.crypt_cbc(self.cbc_iv, bytes(self.private_key, "utf-8"))
            key = str(base64.b64encode(encrypt_value),"utf-8")
            content["encrypt"] = True
        content["private_key"] = key
        content["type"] = "gm"
        with open(filename, "w") as dump_f:
            json.dump(content,dump_f,indent=4)
            dump_f.close()

    #从文件加载，格式是json
    def load_from_file(self, filename, password = None):
        with open(filename, "r") as dump_f:
            content = json.load(dump_f)
            dump_f.close()

        if content["type"] != "gm":
            return
        key  =content["private_key"]
        if password is not None  and len(password) >0 :
            crypt_sm4 = CryptSM4()
            password =self.pwd_ljust(password)
            crypt_sm4.set_key(bytes(password,"utf-8"), SM4_DECRYPT)
            key = base64.b64decode(bytes(key,"utf-8") )
            key = str(crypt_sm4.crypt_cbc(self.cbc_iv, key ),"utf-8")

        self.from_key(key)
