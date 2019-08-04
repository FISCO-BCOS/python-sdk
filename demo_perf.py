'''
  bcosliteclientpy is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/)
  bcosliteclientpy is free software: you can redistribute it and/or modify it under the
  terms of the MIT License as published by the Free Software Foundation. This project is
  distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Thanks for
  authors and contributors of eth-abi, eth-account, eth-hash，eth-keys, eth-typing, eth-utils,
  rlp, eth-rlp , hexbytes ... and relative projects
  @file: transaction_common.py
  @function:
  @author: yujiechen
  @date: 2019-07
'''

from client.common.transaction_common import TransactionCommon
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import random
import time
import sys


class Counter(object):
    def __init__(self):
        self.val = multiprocessing.Value('i', 0)
        self.lock = multiprocessing.Lock()

    def increment(self, n=1):
        with self.lock:
            self.val.value += n

    def value(self):
        return self.val.value


contract_addr = ""
contract_path = "contracts"
contract_name = "Ok"
client = TransactionCommon(contract_addr,
                           contract_path,
                           contract_name)
total_count = int(sys.argv[1])
step = total_count / 10


def sendRequest(recv_counter):
    """
    send trans request
    """
    # generate random number
    trans_num = random.randint(1, 1000)
    fn_name = "trans"
    fn_args = [trans_num]
    client.send_transaction_getReceipt(fn_name, fn_args)
    recv_counter.increment(1)
    if recv_counter.value() % step == 0:
        print("\t\tRecv {}%, tx_num: {}".format(int(recv_counter.value()) / step * 10,
                                                recv_counter.value()))


def main(argv):
    """
    1. deploy Ok.sol
    2. send transactions: set
    """
    # deploy Ok contract
    gasPrice = 30000000
    result = client.send_transaction_getReceipt(None, None, gasPrice, True)[0]
    contract_addr = result['contractAddress']
    client.set_contract_addr(contract_addr)
    executor = ThreadPoolExecutor(max_workers=50)
    counter = 0
    recv_counter = Counter()
    for i in range(0, total_count):
        # task_list.append(counter)
        executor.submit(sendRequest, (recv_counter))
        counter = counter + 1
        if counter % step == 0:
            print("send {}%, tx_num: {}".format(counter / step * 10, counter))
    while recv_counter.value() != total_count:
        time.sleep(1)
    client.finish()


if __name__ == "__main__":
    main(sys.argv[1:])
