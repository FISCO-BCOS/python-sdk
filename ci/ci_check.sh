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

# build blockchain
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
    local contract_addr=$(execute_cmd "python console.py deploy HelloWorld save | grep "address:" | awk -F':' '{print \$3}' | awk '\$1=\$1'")
    updated_blockNumber=$(getBlockNumber)
    if [ $(($init_blockNumber + 1)) -ne $((updated_blockNumber)) ];then
        LOG_ERROR "deploy contract failed for blockNumber hasn't increased"
    fi
    # test cns precompile
    LOG_INFO "## test CNS precompile"
    LOG_INFO "registerCNS..."
    version="1.0_${updated_blockNumber}"
    execute_cmd "python console.py registerCNS HelloWorld \$contract_addr "\${version}"" 
    LOG_INFO "queryCNSByName..."
    query_addr=$(execute_cmd "python console.py queryCNSByName HelloWorld | grep "ContractAddress"|  tail -n 1 | awk -F':' '{print \$2}' | awk '\$1=\$1'")
    
    if [ $(echo ${query_addr} | tr 'a-z' 'A-Z') != $(echo ${contract_addr} | tr 'a-z' 'A-Z') ];then
        LOG_ERROR "queryCNSByName failed for inconsistent contract address"
    fi
    LOG_INFO "queryCNSByNameAndVersion..."
    query_addr=$(execute_cmd "python console.py queryCNSByNameAndVersion HelloWorld \"\$version\" | grep "ContractAddress"|  awk -F':' '{print \$2}' | awk '\$1=\$1'")
    if [ $(echo ${query_addr} | tr 'a-z' 'A-Z') != $(echo ${contract_addr} | tr 'a-z' 'A-Z') ];then
        LOG_ERROR "queryCNSByName failed for inconsistent contract addresss"
    fi
    # test getBlockByNumber
    execute_cmd "python console.py getBlockByNumber \$((\$updated_blockNumber))"
    # test call HelloWord
    local ret=$(execute_cmd "python console.py call HelloWorld \${contract_addr} \"get\"| grep "Hello" ")
    # check call result
    if [ -z "${ret}" ];then
        LOG_ERROR "call HelloWorld failed!"
    fi
    # test sendtx
    execute_cmd "python console.py sendtx HelloWorld  \${contract_addr} \"set\" \"Hello,FISCO\""
    # check call result
    local ret=$(execute_cmd "python console.py call HelloWorld \${contract_addr} \"get\"| grep "Hello,FISCO"")
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

# test consensus precompile
function test_consensus_precompile()
{
    # get node Id for node1
    node_id=$(execute_cmd "cat nodes/127.0.0.1/node1/conf/node.nodeid")
    # test getSealerList
    LOG_INFO "getSealerList..."
    obtained_node_id=$(execute_cmd "python console.py "getSealerList" | grep ${node_id}")
    if [ -z "${obtained_node_id}" ];then
        LOG_ERROR "getSealerList failed for without node1: ${node_id}"
    fi
    # test removeNode
    LOG_INFO "removeNode..."
    execute_cmd "python console.py \"removeNode\" \${node_id}"
    obtained_node_id=$(python console.py "getSealerList" | grep ${node_id})
    sleep 1s
    if [ ! -z "${obtained_node_id}" ];then
        LOG_ERROR "remove node1: ${node_id} failed"
    fi
    obtained_node_id=$(python console.py "getObserverList" | grep ${node_id})
    if [ ! -z "${obtained_node_id}" ];then
        LOG_ERROR "remove node1: ${node_id} failed"
    fi
    # test addObserver
    LOG_INFO "addObserver..."
    execute_cmd "python console.py \"addObserver\" \${node_id}"
    sleep 1s
    obtained_node_id=$(python console.py "getSealerList" | grep ${node_id})
    if [ ! -z "${obtained_node_id}" ];then
        LOG_ERROR "addObserver for ${node_id} failed for search in sealer list"
    fi
    obtained_node_id=$(python console.py "getObserverList" | grep ${node_id})
    if [ -z "${obtained_node_id}" ];then
        LOG_ERROR "addObserver for: ${node_id} failed"
    fi
    # test addSealer
    execute_cmd "python console.py \"addSealer\" \${node_id}"
    sleep 1s
    obtained_node_id=$(python console.py "getSealerList" | grep ${node_id})
    if [ -z "${obtained_node_id}" ];then
        LOG_ERROR "addObserver for ${node_id} failed"
    fi
    sleep 1s
    obtained_node_id=$(python console.py "getObserverList" | grep ${node_id})
    if [ ! -z "${obtained_node_id}" ];then
        LOG_ERROR "addObserver for: ${node_id} failed  for search in observer list"
    fi
}

function get_config_by_key()
{
    key="${1}"
    value=$(execute_cmd "python console.py \"getSystemConfigByKey\" \${key} | grep \"result\" | awk -F':' '{print \$2}' | awk '\$1=\$1' | awk -F'\"' '{print \$2}'")
    echo "${value}"
}

function set_config_by_key()
{
    key="${1}"
    value="${2}"
    execute_cmd "python console.py \"setSystemConfigByKey\" \${key} \${value}"
}

# test sys_config precompile
function test_sys_config()
{
    LOG_INFO "test_sys_config, key: tx_count_limit..."
    tx_limit=$(get_config_by_key "tx_count_limit")
    if [ "${tx_limit}" != "1000" ];then
        LOG_ERROR "invalid tx_count_limit, should be 1000"
    fi
    updated_tx_limit="500"
    set_config_by_key "tx_count_limit" ${updated_tx_limit}
    tx_limit=$(get_config_by_key "tx_count_limit")
    if [ "${tx_limit}" != "${updated_tx_limit}" ];then
        LOG_ERROR "set tx_count_limit failed, should be ${updated_tx_limit}"
    fi

    set_config_by_key "tx_count_limit" "1000"
    tx_limit=$(get_config_by_key "tx_count_limit")
    if [ "${tx_limit}" != "1000" ];then
        LOG_ERROR "set tx_count_limit failed, should be 1000"
    fi
    LOG_INFO "test_sys_config, key: tx_count_limit Succ"

    # test tx_gas_limit
    LOG_INFO "test_sys_config, key: tx_gas_limit..."
    tx_gas_limit=$(get_config_by_key "tx_gas_limit")
    tx_gas="300000000"
    if [ "${tx_gas_limit}" != "${tx_gas}" ];then
        LOG_ERROR "get tx_gas_limit failed, should be ${tx_gas}"
    fi
    # set tx_gas_limit
    updated_gas="500000000"
    set_config_by_key "tx_gas_limit" "${updated_gas}"
    tx_gas_limit=$(get_config_by_key "tx_gas_limit")
    if [ "${tx_gas_limit}" != "${updated_gas}" ];then
        LOG_ERROR "set tx_gas_limit failed, should be ${updated_gas}"
    fi

    # set tx_gas_limit to tx_gas
    set_config_by_key "tx_gas_limit" "${tx_gas}"
    tx_gas_limit=$(get_config_by_key "tx_gas_limit")
    if [ "${tx_gas_limit}" != "${tx_gas}" ];then
        LOG_ERROR "set tx_gas_limit failed, should be ${tx_gas}"
    fi
}

function test_precompile()
{
    test_consensus_precompile
    test_sys_config
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
    test_precompile
}

function main()
{
   execute_cmd "cp client_config.py.template client_config.py"   
   build_blockchain
   start_nodes
   # callback demo_transaction
   execute_cmd "python demo_transaction.py"
   test_rpc
   test_precompile
   test_channel
   stop_nodes
}
main
