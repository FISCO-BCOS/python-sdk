# Python-SDK for FISCO BCOS 

**- bcosliteclient（python）项目说明**

本项目采用Python开发，用于和开源的金融级区块链底层平台FISCO BCOS( https://www.github.com/FISCO-BCOS/ ) 建立JSONRPC协议的通信。支持版本为FISCO BCOS 2.0 RC1~RC3以及后续版本。

意图是构建一个代码尽量少，逻辑尽情轻，层级尽量浅，结构容易理解，可快速复用二次开发的python语言的客户端，所以命名内嵌了"lite"，也并没有生成正式发行包，仅全部开源代码，采用MIT License，欢迎社区体验、修订、增补优化，打造顺手的FISCO BCOS Python客户端。

封装的接口支持所有FISCO BCOS2.0 JSON RPC定义，支持交易输入输出、event log等abi数据拼装和解析，支持直观的keystore账户管理(创建和加载等)，部署合约后保存最新地址和记录部署历史，基本上是一个简单而完整的fisco bcos 2.0客户端SDK。

实现了一个命令行的console交互，简单配置后可以和节点通过JSON RPC接口通信，创建帐号、部署合约、发送交易查询信息。

运行此客户端前应先安装FISCO BCOS节点，并组成一个可正常运行的链，参见[FISCO BCOS安装](https://fisco-bcos-documentation.readthedocs.io/zh_CN/latest/docs/installation.html)，顺利的话只需不到5分钟，也可以安装[官方控制台](https://fisco-bcos-documentation.readthedocs.io/zh_CN/latest/docs/installation.html#id7)进行体验

## update list：

2019.07:支持FISCO BCOS Channel协议，[Channel协议](https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/design/protocol_description.html#channelmessage)支持证书认证更安全，SDK和节点长连接的双向消息通信更高效，便于SDK接收节点主动推送和通知

----------------------------------------------------------------------------

本项目已经适配的python版本:python 3.6.3, 3.7.x。python 2.7.x适配尚在进行中。

## linux环境准备：

安装和使用，参见本目录下的 [linux_python_setup.md](./linux_python_setup.md)

熟悉pyenv和virtualenv的话应该比较顺利，也可以直接安装python3。强烈推荐多环境python设定。

安装pyenv和virtualenv完成后，参考命令：

	pyenv install 3.7.3 -v 
	
	pyenv shell 3.7.3

	pyenv rehash 

	pyenv virtualenv 3.7.3 blc
	
	pyenv activate blc
	
	pip install --upgrade pip

进入名为pytho 3.7.3 , blc的开发运行环境（blc这个名可替换）

----------------------------------------------------------------------------

## windows环境准备：

1.安装python3.7.3 https://www.python.org/

2.安装virtualenv，使用文档： https://virtualenv.pypa.io/en/latest/userguide/

以下在windows的cmd环境工作

    1.安装命令：pip install virtualenv

    2.建立一个工作目录，如d:\python_env,进入d:\python_env

    3.创建一个独立的python环境: virtualenv blc  ("blc"为环境名，可用其他名字)

    4.运行：blc\Scripts\activate.bat

    5.更新pip: pip install --upgrade pip

可以看到命令行前面多了（blc），独立的名为blc的python环境建立完成

另外，在windows上部分python库依赖Visual C++ 14.0 的库，可以到https://visualstudio.microsoft.com/downloads 下载安装ms的文件解决error: Microsoft Visual C++ 14.0 is required. Get it with "Microsoft Visual C++ Build Tools": https://visualstudio.microsoft.com/downloads/ （注意选择vs 2005即14.0版）或链接: https://pan.baidu.com/s/1ZmDUGZjZNgFJ8D14zBu9og 提取码: zrby （百度云文件不保证一定永久存在） 下载VC的安装

----------------------------------------------------------------------------


## 获取项目代码：

	git clone https://github.com/FISCO-BCOS/python-sdk
	
依次运行：
	
	cd python-sdk

	pip install -r requirements.txt

以上为安装依赖库

修改配置文件。将client_config.py.template复制为client_config.py，修改client_config.py里的值：

    contract_info_file="bin/contract.ini" #保存已部署合约信息的文件
    account_keyfile_path="bin/accounts" #保存keystore文件的路径，在此路径下,keystore文件以 [name].keystore命名
    account_keyfile ="pyaccount.keystore"
    account_password ="123456" #实际使用时建议改为复杂密码
    fiscoChainId=1 #链ID，和要通信的节点*必须*一致
    groupid = 1  #群组ID，和要通信的节点*必须*一致，如和其他群组通信，修改这一项，或者设置bcosclient.py里对应的成员变量
    logdir="bin/logs" #默认日志输出目录，该目录必须先建立
    #---------client communication config--------------
    client_protocal = "rpc"  # or "channel" to use channel prototal
    remote_rpcurl = "http://127.0.0.1:8545"  # 采用rpc通信时，节点的rpc端口,和要通信的节点*必须*一致，,**如采用channel协议通信，这里可以留空**
    channel_host="127.0.0.1" #采用channel通信时，节点的channel ip地址,**如采用rpc协议通信，这里可以留空**
    channel_port=20200  ##节点的channel 端口,**如采用rpc协议通信，这里可以留空**
    channel_ca="bin/ca.crt"  #采用channel协议时，需要设置链证书,**如采用rpc协议通信，这里可以留空**
    channel_node_cert="bin/node.crt"  #采用channel协议时，需要设置节点证书,**如采用rpc协议通信，这里可以留空**
    channel_node_key="bin/node.key"   #采用channel协议时，需要设置节点key,**如采用rpc协议通信，这里可以留空**

**注意**

1.首先请确保端口是开放的，可以本机或远程访问（如在防火墙后，则需要在防火墙上开通端口规则）,可以先使用telnet [ip] [port]指令（如telnet 127.0.0.1 8545或telnet 127.0.0.1 20200）确认网络连通ok。

2.采用RPC方式连接，不需要设置证书，直接使用明文json协议，和RPC端口通信。

3.如使用了channel协议，需要从节点的sdk目录下获取ca.crt,node.crt,node.key这三个文件，复制到python-sdk/bin目录下,这三个文件用于channel协议通信时，建立TLSv1.2安全连接握手。

如需要连接的节点部署的目录在/data/fisco-bcos/nodes/127.0.0.1/,当前目录已经在python-sdk目录下，则

    cp /data/fisco-bcos/nodes/127.0.0.1/sdk/ca.crt ./bin
    cp /data/fisco-bcos/nodes/127.0.0.1/sdk/node.crt ./bin
    cp /data/fisco-bcos/nodes/127.0.0.1/sdk/node.key ./bin
	
修改配置后，运行一个简单命令确认和节点连接是否正常

	python console.py getNodeVersion

如能读到节点版本信息，那么两者连接是ok的。


**如报告Crypto包不存在，进入virtualenv的目录如d:\python_env\blc\lib\site-packages\,将小写的crypto目录名第一个字母改为大写Crypto （这貌似是windows环境的一个坑,linux上不存在这个问题)**

**由于不同环境操作系统依赖，python版本，网络情况有所不同，如自动安装依赖部分不成功，可通过pip install [指定模块]的方式尝试安装**


logger配置参见client/clientlogger.py。默认在bin/logs下生成滚动日志，包括客户端日志和统计日志两种，默认级别为DEBUG

----------------------------------------------------------------------------

## 合约相关：

后缀名为.sol的solidity合约代码文件（本客户端不实现编译功能，sol文件仅供参考查看），请采用fisco-bcos的控制台，[对合约sol代码文件进行编译](https://fisco-bcos-documentation.readthedocs.io/zh_CN/latest/docs/tutorial/sdk_application.html?highlight=%E7%BC%96%E8%AF%91#id7)

合约编译后，在控制台console/contracts/sdk目录以及对应子目录下，有对应指定合约且后缀名为.abi,.bin的文件，将其复制到本客户端的contracts目录下，bin文件供console.py和demo_transaction.py用于部署合约,abi文件则用于调用接口、解析数据。

控制台console.py和demo_transaction.py都默认从contracts目录下按指定名字加载abi信息，如需放到别的目录下，可直接修改这两个文件里的相关定义。

abi文件定义了合约的事务方法，只读方法，事件等，只要得知abi,即可采用console.py，指定方法名，合约地址，正确的参数列表，调用abi里定义的方法。不需要类似java客户端那样再生成一组面向特定合约的客户端代码组件。

如SimpleInfo.sol合约里定义了 
   
    function set(string n,uint256 b,address a) public returns(int)

对应的命令是 
    
    python console.py sendtx set SimpleInfo [合约部署到链上的地址] name  100  0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC

对只读方法的调用示例 
    
    python console.py call SimpleInfo [合约部署到链上的地址]  getall

注意，console.py 对事务方法和只读方法两者的调用,使用不同的关键字sendtx/call。

----------------------------------------------------------------------------


## 本项目提供可执行的应用如下，均基于client/bcosclient.py基础组件建立：

### 1 体验应用-->

demo_client.py和demo_get.py演示调用client/bcosclient.py里实现的接口，demo_client.py演示部署/交易/call流程，demo_get.py已经实现FISCO BCOS2.0的所有rpc查询接口(如面向一条新链运行，那么有可能获取不到部分区块和交易等信息导致报错，是正常的，可打开该文件修改输入参数，查询指定的区块和交易)

### 2 console.py 控制台应用-->

首先运行

	python console.py usage 

查看已经实现的命令，包括创建帐号，delploy/call/sendtx，JSON RPC查询接口等

**采用创建帐号的命令创建帐号后，如需要做为默认帐号使用，注意修改client_config.py的account_keyfile和account_password配置项**

	1): showaccount [name] [password]
		指定帐户名字(不带后缀)和密码，打开配置文件里默认账户文件路径下的[name].keystore文件，打印公私钥和地址


	2): newaccount [name] [password] [save]
		创建一个新帐户，参数为帐户名(如alice,bob)和密码
		结果加密保存在配置文件指定的帐户目录 *如同目录下已经有同名帐户文件，旧文件会复制一个备份
		如输入了"save"参数在最后，则不做询问直接备份和写入
		create a new account ,save to :[bin/accounts] (default) , the path in client_config.py:[account_keyfile_path]
		if account file has exist ,then old file will save to a backup
		if "save" arg follows,then backup file and write new without ask

	3): deploy [contract_binary_file] [save]
		部署合约,合约来自编译后的bin文件（部署命令为了审慎起见，需要指定bin文件的全路径）。如给出'save'参数，新地址会写入本地记录文件
		ndeploy contract from a binary file,eg: deploy contracts/SimpleInfo.bin
		if 'save' in args, so save addres to file

	4): call [contractname] [address] [func]  [args...]
		call合约的一个只读接口,解析返回值
		call a constant funciton of contract and get the returns
		eg: call SimpleInfo 0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC getbalance1 11
		if address is "last" ,then load last address from :bin/contract.ini
		eg: call SimpleInfo last getall


	5): sendtx [contractname]  [address] [func] [args...]
		发送交易调用指定合约的接口，交易如成功，结果会写入区块和状态
		send transaction,will commit to blockchain if success
		eg: sendtx SimpleInfo 0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC set alice 100 0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC
		if address is "last" ,then load last address from :bin/contract.ini
		eg: sendtx SimpleInfo last set 'test' 100 '0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC'


	6): all the 'get' command for JSON RPC
		各种get接口，查询节点的各种状态（不一一列出，可用list指令查看接口列表和参数名）
		neg: [getBlockByNumber 10 true].
		use 'python console.py list' to show all get cmds

	7): list
		列出所有支持的get接口名和参数
		list: list all  getcmds  has implemented (getBlock...getTransaction...getReceipt..getOthers)

	8): int [hex number]
		输入一个十六进制的数字，转为十进制（考虑到json接口里很多数字都是十六进制的，所以提供这个功能）
		convert a hex str to int ,eg: int 0x65

	9): txinput [contractname] [inputdata(in hex string)]
		复制一段来自transaction的inputdata(十六进制字符串)，指定合约名，则可以自动解析（合约的abi文件应存在指定目录下）
		parse the transaction input data by  contractname，eg: txinput SimpleInfo [txinputdata]

	10): checkaddr [address]
		将普通地址转为自校验地址,自校验地址使用时不容易出错
		change address to checksum address according EIP55:
		to_checksum_address: 0xf2c07c98a6829ae61f3cb40c69f6b2f035dd63fc -> 0xF2c07c98a6829aE61F3cB40c69f6b2f035dD63FC
		
----------------------------------------------------------------------------
## 主要基础模块

**client/bcosclient.py** 客户端SDK，封装了加载配置，JSON RPC接口等。

**client/bcostransaction.py** 根据bcos对交易数据结构的定义，增加字段，修改拼装方法，实现交易编码.client/transaction.py为原以太坊交易格式的实现。

**eth_account/account.py** 实现帐户的创建，保存，加载等（加密和解密帐户keystore文件约需1s以上）

**client/contratnote.py** 采用ini配置文件格式保存合约的最新地址和历史地址，以便加载（如console命令里可以用(合约名 last)指代某个合约最新部署的地址）

**client/datatype_parser.py** 管理abi，用function名和4字节selector定位查找到合约function的abi，提供一系列数据解析接口，解析receipt log,tx input/output等

**client/clientlogger.py** logger定义，目前包括客户端日志和统计日志两种

**client/stattool.py** 一个简单的统计数据收集和打印日志的工具类

**client/ChannelPack.py** FISCO BCOS channel协议编码解码工具类,channel协议编解码参见[连接](https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/design/protocol_description.html#channelmessage)

**client/ChannelHandler.py** FISCO BCOS channel协议实现类，包括TLSv1.2认证，发送和接收线程和消息队列实现,channel协议是sdk和节点之间长连接和双向消息协议,处理起来比RPC复杂但更高效，支持证书认证，更安全，长连接便于接收即节点主动通知

**bcosclient.py** 里实现的发送交易接口为：

    deploy：部署合约

    call： 调用合约接口，返回只读的数据

    sendRawTransaction：返回transactionHash

    sendRawTransactionGetReceipt : 发送交易后等待共识完成，检索receipt，

sendRawTransaction这两个方法可用于所有已知abi的合约，传入abi定义，方法名，正确的参数列表，即可发送交易。交易由BcosClient里加载的账号进行签名。

查询方法均为get开头，输入参数根据查询的内容略有不同，如getBlockByNum为“”高度”和"是否加载交易列表"两个参数。

----------------------------------------------------------------------------

## 解析数据

面向transaction，receipt，可采用datatypes/datatypeparse.py里实现的DatatypeParser对象的方法。

主要方法有：

    parse_abi: 将abi文件里的function和event解析为字典索引，其中function的索引方式为name和4字节selector两种，供后续查询.func_abi_map_by_selector,func_abi_map_by_name,event_abi_map这几个dict即为字典索引对象     

    parse_transaction_input: 用于transaction，用于查询交易后解析input数据（方法+参数）

    parse_receipt_output： 用于receipt，解析合约接口的返回值

    parse_event_logs：用于receipt，解析eventlog数组，增加eventname，eventdata两个数据


和abi基础数据结构操作有关的方法分布在多个模块, 详细实现可查询代码

	from eth_abi import(
		encode_single,  #输入abi定义如("unit256","string")，进行数据编码
		encode_abi, #即将废弃,输入类型为["unit256","string"],都用encode/decode_single就好
		decode_single, #对应encode_singile ，对数据进行解码
		decode_abi  #即将废弃
		)
		
	from eth_utils import (
		function_signature_to_4byte_selector, #输入方法abi，输出4字节的selector
		event_abi_to_log_topic,  #输入event的abi，输出event里的topic串
		encode_hex,decode_hex #16进制串编解码
		)

	from utils.abi import  (
		filter_by_type, #通过类型选择一组元素，如"function","event"等
		abi_to_signature, #输入方法名，输出可读的方法定义如 "set(uint256,string)"
		get_abi_output_types, #获取abi的输出定义
		get_fn_abi_types, #获取abi的输入输出定义,适配encode_abi/decode_abi，用参数“inputs” "outpus"选择
		get_fn_abi_types_single,#获取abi的输入输出定义，适配encode_single/decde_single，用参数“inputs” "outpus"选择
		exclude_indexed_event_inputs, #排除event定义中声明为indexed的参数，这些参数不进入logs数据里只存在于topics里
		exclude_indexed_event_inputs_to_abi, #声明为indexed之外的参数，封装为encode_abi/decode_abi接受的参数
		exclude_indexed_event_inputs_to_single,#声明为indexed之外的参数，封装为encode_single/decode_single接受的参数
		)

----------------------------------------------------------------------------

## 开源说明

此项目源自开源，响应开源，可在符合license前提下自由使用和分发。其中eth-abi，eth-account，eth-hash，eth-keys，eth-typing，eth-utils，rlp, eth-rlp , hexbytes等都为开源项目，各子目录都保留了license,README，向原作者（们）致谢！
(是的，兼容evm，复用了abi/rlp编码，但底层项目实际上整个架构已经重写)


以上引用的代码有修订，为了便于修改，所以将这些项目并入代码目录，不采用发布包的方式引用。


本工程从开始准备到初版完成历时一周，主要在工作之余的碎片时间和深夜完成，得益于开源社区既有代码的基础以及python语言的开发效率,所写代码不多，主要是发掘可用api和进行整理、重构、胶水式组合封装(准备和整理环境的时间，简直比写关键代码耗时还长:P)。欢迎体验和PR,一起持续更新维护。

todolist: 

    1：更友好的交互和提示
    2：和节点之间的异步通信
    3：节点事件监听
    4：Channel协议支持 (2019.07实现)
	5：AMOP topic协议支持
    5：性能优化
