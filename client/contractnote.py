'''
  bcosliteclientpy is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/FISCO-BCOS)
  bcosliteclientpy is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Free Software Foundation
  This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE
  Thanks for authors and contributors of eth-abi，eth-account，eth-hash，eth-keys，eth-typing，eth-utils，rlp, eth-rlp , hexbytes ...and relative projects
  @author: kentzhang
  @date: 2019-06
'''
from client_config import client_config
from configobj import  ConfigObj

class ContractNote:
    @staticmethod
    def get_last(name):
        config = ConfigObj(client_config.contract_info_file, encoding='UTF8')
        if name in config["address"]:
            address = config["address"][name]
        else:
            address = None
        return address

    @staticmethod
    def save_address(contractname, newaddress, blocknum=None, memo=None):
        from configobj import ConfigObj
        import time
        #write to file
        config = ConfigObj(client_config.contract_info_file,
                           encoding='UTF8')
        if "addess" not in config:
            config['address']={}
        config['address'][contractname] = newaddress
        #print (config)
        if blocknum!=None:
            if "history" not in config:
                config["history"]={}
            timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime());
            detail="{}:{},block:{}".format(contractname,timestr,blocknum)
            if memo !=None: #
                detail="{},{}".format(detail,memo)
            config["history"][newaddress] = detail
        config.write()
