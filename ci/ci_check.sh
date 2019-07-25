#!/bin/bash

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
  # get_buildchain.sh may fail due to access github api failed
  #bash <(curl -s https://raw.githubusercontent.com/FISCO-BCOS/FISCO-BCOS/dev/tools/get_buildchain.sh)
  
  if [ ! -f "build_chain.sh" ];then
     LOG_ERROR "get build_chain.sh failed!"
  fi
  execute_cmd "chmod a+x build_chain.sh"
  # build the blockchain
  ./build_chain.sh -l "127.0.0.1:4"
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

function getBlockNumber()
{
    execute_cmd "python console.py getBlockNumber | grep blockNumber | awk -F':' '{print \$2}' | awk '\$1=\$1'"
}

# test the common jsonRPC interface
function test_common_rpcInterface()
{
   LOG_INFO "## test commonRPCInterface..."
   # getNodeVersion
   execute_cmd "python console.py getNodeVersion"
   # usage
   execute_cmd "python console.py usage"
   # list
   execute_cmd "python console.py list"
   # demo_get
   execute_cmd "python demo_get.py"
   LOG_INFO "## test commonRPCInterface finished..."
} 

# test the contract
function test_contract()
{
    LOG_INFO "## test contract..."
    init_blockNumber=$(getBlockNumber)
    # deploy and get contract address
    local contract_addr=$(execute_cmd "python console.py deploy contracts/HelloWorld.bin save | grep "address:" | awk -F':' '{print \$3}'")
    #execute_cmd "python console.py deploy contracts/HelloWorld.bin save"
    updated_blockNumber=$(getBlockNumber)
    if [ $(($init_blockNumber + 1)) -ne $((updated_blockNumber)) ];then
        LOG_ERROR "deploy contract failed for blockNumber hasn't increased"
    fi

    # test getBlockByNumber
    execute_cmd "python console.py getBlockByNumber \$((\$updated_blockNumber))"

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
    LOG_INFO "## test contract finished..."
}

# test account
function test_account()
{
    LOG_INFO "## test account..."
    local file_path="bin/accounts/test_account.keystore"
    execute_cmd "rm -rf \${file_path}"
    # new account
    LOG_INFO ">> test newaccount..."
    local addr=$(execute_cmd "python console.py newaccount test_account "123456" | grep "address" | grep -v "new" | awk -F':' '{print \$2}' | awk '\$1=\$1'")
    if [ ! -f "${file_path}" ];then
        LOG_ERROR "new account failed!"
    fi

    # show account
    LOG_INFO ">> test showaccount..."
    local addr2=$(execute_cmd "python console.py showaccount test_account \"123456\" | grep "address" | grep -v "new" | awk -F':' '{print \$2}' | awk '\$1=\$1'")
    
    # check address
    if [ "${addr}" != "${addr2}" ];then
        LOG_ERROR "check newaccount/showaccount failed for inconsistent store/load address, store_addr: ${addr}, load_addr: ${addr2}"
    fi
    LOG_INFO "## test account finished..."
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
   # callback demo_transaction
   execute_cmd "python demo_transaction.py"
   test_rpc
   test_channel
   stop_nodes   
}
main
