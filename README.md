# Python SDK

![](./images/FISCO_BCOS_Logo.svg)


[![Build Status](https://travis-ci.org/FISCO-BCOS/python-sdk.svg?branch=master)](https://travis-ci.org/FISCO-BCOS/python-sdk)
[![CodeFactor](https://www.codefactor.io/repository/github/fisco-bcos/python-sdk/badge)](https://www.codefactor.io/repository/github/fisco-bcos/python-sdk)
![GitHub All Releases](https://img.shields.io/github/downloads/FISCO-BCOS/python-sdk/total.svg)
[![GitHub license](https://img.shields.io/github/license/FISCO-BCOS/python-sdk.svg)](https://github.com/FISCO-BCOS/python-sdk/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/FISCO-BCOS/python-sdk.svg)](https://github.com/FISCO-BCOS/python-sdk/issues)
--- 

Python SDK为[FISCO BCOS](https://github.com/FISCO-BCOS/FISCO-BCOS/tree/master)提供Python API，使用FISCO BCOS Python SDK可以简单快捷的基于FISCO-BCOS进行区块链应用开发。**此版本只支持**[FISCO BCOS 2.0](https://fisco-bcos-documentation.readthedocs.io/zh_CN/latest/)。


## 关键特性

- 提供调用FISCO BCOS 2.0 [JSON-RPC](https://fisco-bcos-documentation.readthedocs.io/zh_CN/latest/docs/api.html)的Python API。
- 可基于[Channel协议](https://fisco-bcos-documentation.readthedocs.io/zh_CN/latest/design/protocol_description.html#channelmessage)与FISCO BCOS进行通信，保证节点与SDK安全加密通信的同时，可接收节点推送的消息。
- 支持交易解析功能：包括交易输入、交易输出、Event Log等ABI数据的拼装和解析。
- 支持合约编译，将`sol`合约编译成`abi`和`bin`文件。
- 支持基于keystore的账户管理。
- 支持合约历史查询。

## 部署Python SDK

**环境要求**
- Python环境：python 3.6.3, 3.7.x
- FISCO BCOS节点：请参考[FISCO BCOS安装](https://fisco-bcos-documentation.readthedocs.io/zh_CN/latest/docs/installation.html#fisco-bcos)搭建

**依赖软件**

- **Ubuntu**: `sudo apt install -y zlib1g-dev libffi6 libffi-dev`
- **CentOS**：`sudo yum install -y zlib-devel libffi-devel`


**拉取源代码**

```bash
git clone https://github.com/FISCO-BCOS/python-sdk
```

**初始化环境(若python环境符合要求，可跳过)**

```bash
# 判断python版本，并为不符合条件的python环境安装python 3.7.3的虚拟环境，命名为python-sdk
# 若python环境符合要求，可以跳过此步
# 若脚本执行出错，请检查是否参考[依赖软件]说明安装了依赖
# 提示：安装python-3.7.3可能耗时比较久
cd python-sdk && bash init_env.sh

# 激活python-sdk虚拟环境
source ~/.bashrc && pyenv activate python-sdk
```

**安装依赖**


```bash
pip install -r requirements.txt
```
**若因网络原因，安装依赖失败，可使用清华的pip源下载，安装命令如下：**

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

**拷贝配置**
```bash
cp client_config.py.template client_config.py
```

**SDK使用示例**
```bash
# 查看SDK使用方法
./console.py usage

# 获取节点版本
./console.py getNodeVersion
```

**部署HelloWorld合约**
```bash
$ ./console.py deploy contracts/HelloWorld.bin
>> user input : ['deploy', 'contracts/HelloWorld.bin', 'save']

deploy result  for [contracts/HelloWorld.bin] is:
 {
    "blockHash": "0xa9238a4138b5cac925d2d7b338c44acca5c1ae4d83df2243159cef4ff89c8c66",
     ... 省略若干行...
    "transactionIndex": "0x0"
}
on block : 8,address: 0x42883e01ac97a3a5ef8a70c290abe0f67913964e 
```

**调用HelloWorld合约**

```bash
# 调用get接口
$./console.py call HelloWorld 0x42883e01ac97a3a5ef8a70c290abe0f67913964e get

>> user input : ['call', 'HelloWorld', '0x42883e01ac97a3a5ef8a70c290abe0f67913964e', 'get']

param formatted by abi: []
call HelloWorld , address: 0x42883e01ac97a3a5ef8a70c290abe0f67913964e, func: get, args:[]
call result:  'Hello, World!'

# 调用set接口
$./console.py sendtx HelloWorld 0x42883e01ac97a3a5ef8a70c290abe0f67913964e "Hello, FISCO"
> user input : ['sendtx', 'HelloWorld', '0x42883e01ac97a3a5ef8a70c290abe0f67913964e', 'set', 'Hello, FISCO']

param formatted by abi: ['Hello, FISCO']
sendtx HelloWorld , address: 0x42883e01ac97a3a5ef8a70c290abe0f67913964e, func: set, args:['Hello, FISCO']
sendtx receipt:  {
    "blockHash": "0x44d00ec42fe8abe12f324ceea786e065c095ecef1116fdc3b7ce4b38618de5d6",
    ... 省略若干行...
    "transactionIndex": "0x0"
}

>>  receipt logs : 
>> transaction hash :  0x7e7f56c656a743b6b052fff8d61901a9ea752f758084fc3ef2fdc9a854f597d4
tx input data detail:
 {'name': 'set', 'args': ('Hello, FISCO',), 'signature': 'set(string)'}
receipt output : ()

# 调用get接口获取更新后字符串
$./console.py call HelloWorld 0x42883e01ac97a3a5ef8a70c290abe0f67913964e get

>> user input : ['call', 'HelloWorld', '0x42883e01ac97a3a5ef8a70c290abe0f67913964e', 'get']

param formatted by abi: []
call HelloWorld , address: 0x42883e01ac97a3a5ef8a70c290abe0f67913964e, func: get, args:[]
call result:  'Hello, FISCO!'
```

## 开启命令行自动补全

Python SDK引入[argcomplete](https://argcomplete.readthedocs.io/en/latest/)支持命令行补全，运行如下命令开启此功能(**bashrc仅需设置一次，设置之后每次登陆自动生效**)

```bash
echo "eval \"\$(register-python-argcomplete ./console.py)\"" >> ~/.bashrc
source ~/.bashrc
```

## 文档

[**中文**](https://fisco-bcos-documentation.readthedocs.io/zh_CN/feature-python-sdk/docs/sdk/python_sdk/index.html)

## 贡献代码
欢迎参与FISCO BCOS的社区建设：
- 如项目对您有帮助，欢迎点亮我们的小星星(点击项目左上方Star按钮)。
- 提交代码(Pull requests)，参考我们的[代码贡献流程](CONTRIBUTING_CN.md)。
- [提问和提交BUG](https://github.com/FISCO-BCOS/python-sdk/issues/new)。
- 如果发现代码存在安全漏洞，请在[这里](https://security.webank.com)上报。
- 在[微信群](https://github.com/FISCO-BCOS/FISCO-BCOS-DOC/blob/release-2.0/images/community/WeChatQR.jpg)和[Gitter](https://gitter.im/fisco-bcos/Lobby)参与讨论。


## 加入社区
[![](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Follow@FiscoBcos)](https://twitter.com/FiscoBcos)
[![Gitter](https://img.shields.io/badge/style-on_gitter-green.svg?logo=gitter&longCache=false&style=social&label=Chat)](https://gitter.im/fisco-bcos/Lobby)
[![](https://img.shields.io/twitter/url/http/shields.io.svg?logo=Gmail&style=social&label=service@fisco.com.cn)](mailto:service@fisco.com.cn)

FISCO BCOS开源社区是国内活跃的开源社区，社区长期为机构和个人开发者提供各类支持与帮助。已有来自各行业的数千名技术爱好者在研究和使用FISCO BCOS。如您对FISCO BCOS开源技术及应用感兴趣，欢迎加入社区获得更多支持与帮助。

![](https://media.githubusercontent.com/media/FISCO-BCOS/LargeFiles/master/images/QR_image.png)

## License
![license](https://img.shields.io/github/license/FISCO-BCOS/python-sdk.svg)

Python SDK的开源协议为[MIT License](https://opensource.org/licenses/MIT). 详情参考[LICENSE](./LICENSE)。
