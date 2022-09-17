支持FISCO BCOS 3.x接口: [JSON-RPC](https://fisco-bcos-doc.readthedocs.io/zh_CN/latest/docs/develop/api.html)。对于FISCO BCOS3.x，客户端采用Python包装C语言开发的底层SDK库，由SDK库负责网络协议封装和安全通信细节。


## 代码实现
在bcos3sdk目录:

- bcos3sdk_wrap.py : 将C语言库包装到Python的实现，基本上是对[C语言SDK的接口](https://fisco-bcos-doc.readthedocs.io/zh_CN/latest/docs/develop/sdk/c_sdk/api.html)逐一进行映射，熟悉python ctypes的话看起来毫无压力
- bcos3client.py : 基于bcos3sdk_wrap.py,增加可配置特性，适当简化接口

其他
- console3.py : 面向FISCO BCOS 3.x的控制台入口文件
- console_utils/cmd_bcos3_transaction,cmd_bcos3_rpc 等包含"bcos3"关键字的文件，是面向控制台的命令实现，基本上就是解析输入参数，调用bcos3client.py,并在屏幕上打印信息


## 编解码实现

- 面向合约的abi编解码采用Python实现，这部分FISCO BCOS 3.x和2.x没有区别
- 面向通信的协议编解码采用开源tars框架协议，不再适用2.x的RLP。由底层库实现，在python层无需关注细节。


## FISCO BCOS 3.x 配置和库文件下载

FISCO BCOS 3.x相关配置也在client_config.py文件里，大部分和2.x的一致。

只需要关注以下几个字段：
```bash
    # FISCO BCOS3.0的配置段，如连接FISCO BCOS2.0版本，无需关心此段
    # FISCO BCOS3.0 c底层sdk的配置，都在bcos3_config_file里，无需配置在此文件
    bcos3_lib_path ="./bcos3sdklib"
    bcos3_config_file ="./bcos3sdklib/bcos3_sdk_config.ini"
    group = "group0"
```

由于FISCO BCOS 3.x提供了SDK的C语言库，诸多细节封装在库里，也引入了独立的配置文件，即上面配置里的bcos3_config_file。包括

默认放在 bcos3sdklib目录(可参照上方的配置项修改) **bcos3_sdk_config.ini**,节点证书、SDK证书、节点IP端口等信息在该文件里配置

默认放在当前目录下的 **clog.ini**，供sdk打日志配置使用

**重要:**

最新版本的C语言的SDK库文件可到[文件下载连接](https://fisco-bcos-doc.readthedocs.io/zh_CN/latest/docs/develop/sdk/c_sdk/dylibs.html),下载相应操作系统的库文件。

建议下载后放到当前目录的 ./bcos3sdklib 目录下，供python代码调用。

 