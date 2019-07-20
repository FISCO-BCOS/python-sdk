
**合约的编译方式包括**

    1) 操作系统类型，linux/windows 
    2) 合约所用的solidity语言版本，如0.4.x或0.5.2+
    3) 是否国密版本

**操作次序：**

    1.在以下链接中选择对应的release发布包，下载到python-sdk/bin/solc目录
    2.将下载的文件解压（如为压缩包）并将编译器执行文件改名为solc。
    3.确认python-sdk/solc.py 文件里对solc名字或路径的定义和这里的solc能完全匹配，总之目的是使得编译命令行一定能找到对应的solc，设置为系统path变量也是可以的。

according system(linux/windows)and solidity contract version，download the solc binary release,save to python-sdk/bin/solc/,unzip(optional), and change binary file name to "solc",or change the solc path in python-sdk/solcpy.py file

## solc release on github:
    
    https://github.com/FISCO-BCOS/solidity/releases

## linux:
**for solidity >= 0.5.2**
    
    https://github.com/FISCO-BCOS/solidity/releases/download/v0.5.2/solc-linux

gm version :
    
    centos: https://github.com/FISCO-BCOS/solidity/releases/download/v0.5.2/solc-gm-centos
    ubuntu: https://github.com/FISCO-BCOS/solidity/releases/download/v0.5.2/solc-gm-ubuntu

**for solidity <= 0.5.0**
    
    https://github.com/FISCO-BCOS/solidity/releases/download/v0.4.25/solc-static-linux

gm version:
    
    https://github.com/FISCO-BCOS/solidity/releases/download/v0.4.25/solc-gm-static-linux


## windows

**for solidity >= 0.5.2**
    
    https://github.com/FISCO-BCOS/solidity/releases/download/v0.5.2/solc-windows.zip

gm version:
    
    https://github.com/FISCO-BCOS/solidity/releases/download/v0.5.2/solc-gm-windows.exe

**for solidity <= 0.5.0**
    
    https://github.com/FISCO-BCOS/solidity/releases/download/v0.4.25/solc-windows.zip

gm version:
    
    https://github.com/FISCO-BCOS/solidity/releases/download/v0.4.25/solc-gm-windows.exe


