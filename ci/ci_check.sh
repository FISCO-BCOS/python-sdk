#!/bin/bash

version="2.0.0"
node_num=4

LOG_ERROR()
{
    local content=${1}
    echo -e "\033[31m[ERROR] ${content}\033[0m"
    exit 1
}

execute_cmd()
{
    command="${1}"
    #LOG_INFO "RUN: ${command}"
    eval ${command}
    ret=$?
    if [ $ret -ne 0 ];then
        LOG_ERROR "FAILED execution of command: ${command}"
	if [ -d "nodes" ];then
	   bash nodes/127.0.0.1/stop_all.sh && rm -rf nodes
        fi
    fi
}

LOG_INFO()
{
    local content=${1}
    echo -e "\033[32m[INFO] ${content}\033[0m"
}

cur_path=$(execute_cmd "pwd")

# build blockchan
function build_blockchain()
{
  execute_cmd "rm -rf nodes"
  # download build_chain.sh
  execute_cmd "curl -LO https://raw.githubusercontent.com/FISCO-BCOS/FISCO-BCOS/master/tools/build_chain.sh && chmod u+x build_chain.sh"
  # download fisco-bcos
  #bash <(curl -s https://raw.githubusercontent.com/FISCO-BCOS/FISCO-BCOS/master/tools/ci/download_bin.sh) -b release-${version}
  # build the blockchain
  execute_cmd "./build_chain.sh -l "127.0.0.1:${node_num}" -v ${version}"
  # copy certificate
  execute_cmd "cp nodes/127.0.0.1/sdk/* bin/"
}

# start the nodes
function start_nodes()
{
   execute_cmd "./nodes/127.0.0.1/start_all.sh"
}

# stop the nodes
function stop_nodes()
{
   execute_cmd "./nodes/127.0.0.1/stop_all.sh"
}

# test the common jsonRPC interface
function test_common_rpcInterface()
{
   # getNodeVersion
   execute_cmd "python console.py getNodeVersion"
   # usage
   execute_cmd "python console.py usage"
   # list
   execute_cmd "python console.py list"
} 

# test the contract
function test_contract()
{
    # test deploy HelloWord contract
    execute_cmd "python console.py deploy contracts/HelloWorld.bin save"
    # get contract address
    local contract_addr=$(execute_cmd "python console.py deploy contracts/HelloWorld.bin save | grep "address:" | awk -F':' '{print \$3}'")
    # test call HelloWord
    local ret=$(execute_cmd "python console.py call HelloWorld \${contract_addr} \"get\" | grep "Hello" ")
    # check call result
    if [ -z "${ret}" ];then
        LOG_ERROR "call HelloWorld failed!"
    fi
    # test sendtx
    execute_cmd "python console.py sendtx HelloWorld  \${contract_addr} \"set\" \"Hello,FISCO\""
    # check call result
    local ret=$(execute_cmd "python console.py call HelloWorld \${contract_addr} \"get\" | grep "Hello,FISCO"")
    # check result
    if [ -z "${ret}" ];then
        LOG_ERROR "sendtx failed to set HelloWorld failed!"
    fi
}

# test account
function test_account()
{
    local file_path="bin/accounts/test_account.keystore"
    execute_cmd "rm -rf \${file_path}"
    # new account
    # python console.py newaccount new_account "123456" | grep "address" | grep -v "new" | awk -F':' '{print $2}' | awk '$1=$1'
    local addr=$(execute_cmd "python console.py newaccount test_account "123456" | grep "address" | grep -v "new" | awk -F':' '{print \$2}' | awk '\$1=\$1'")
    if [ ! -f "${file_path}" ];then
        LOG_ERROR "new account failed!"
    fi

    # show account
    local addr2=$(execute_cmd "python console.py showaccount test_account \"123456\" | grep "address" | grep -v "new" | awk -F':' '{print \$2}' | awk '\$1=\$1'")
    
    # check address
    if [ "${addr}" != "${addr2}" ];then
        LOG_ERROR "check newaccount/showaccount failed for inconsistent store/load address, store_addr: ${addr}, load_addr: ${addr2}"
    fi
}

# test_rpc
function test_rpc()
{
    test_common_rpcInterface
    test_contract
    test_account
}

# test channel
function test_channel()
{
    # update config to channel
    sed -i "s/client_protocol = \"rpc\"/client_protocol = \"channel\"/g" client_config.py
    test_rpc
}

function main()
{
   execute_cmd "cp client_config.py.template client_config.py"   
   build_blockchain
   start_nodes
   test_rpc
   test_channel
   stop_nodes   
}
main
