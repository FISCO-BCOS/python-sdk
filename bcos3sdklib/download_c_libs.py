import sys
sys.path.append("..")
import os
import time
import platform

from bcos3sdk.bcos3client import Bcos3Client


from client import filedownloader
#基础下载站，有可能可以换成gitee
base_url = "https://github.com/FISCO-BCOS/bcos-c-sdk/releases/download"
#版本号，可以动态更新，实际上加到url时，前面会加个v，如v3.4.0
version = "3.4.0"
#网络代理，下载时可能需要使用
net_proxy=[]

# sample:  设置代理
net_proxy = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
}

win_dll_name = "bcos-c-sdk.dll"
win_lib_name = "bcos-c-sdk.lib"
linux_aarch64_name = "libbcos-c-sdk-aarch64.so"
linux_lib_name = "libbcos-c-sdk.so"
mac_m1_aarch64_dylib_name = "libbcos-c-sdk-aarch64.dylib"
mac_x64_lib_name = "libbcos-c-sdk.dylib"

file_list= []
platsys = platform.platform().lower()
print("Platform is ",platsys)
if platsys.startswith("win"):  # Windows
    file_list.append(win_lib_name)
    file_list.append(win_dll_name)
elif "mac" in platsys:  # Mac
    if "arm64" in platsys:  # mac m1
        file_list.append(mac_m1_aarch64_dylib_name)
    else:  # mac x86
        file_list.append(mac_x64_lib_name)
elif "linux" in platsys:  # Linux
    if "arm64" in platsys or "aarch64" in platsys:
        file_list.append(linux_aarch64_name)
    elif "x86_64" in platsys:  # linux x86
        file_list.append(linux_lib_name)
    else:  # unknown arch
        raise Exception('''Unsupported linux arch {}'''.format(platsys))
else:  # unknown os
    raise Exception('''Unsupported os {}'''.format(platsys))

#开始下载一到多个文件到当前目录。如果当前目录有文件，那么要注意备份
for fname in file_list:
    url = f"{base_url}/v{version}/{fname}"
    print("download: ",url)
    filedownloader.download_file_with_progress(url,fname,proxies=net_proxy)
    if not os.path.exists(fname):
        print(f"! Download Fail ,File NOT Exist {fname},from {url}")
    else:
        stats = os.stat(fname)
        #mtime_local = time.localtime(stats.st_mtime)
        #mtime_str  = time.strftime('%Y-%m-%d %H:%M:%S',mtime_local)
        print(f"file {fname} ,size {int(stats.st_size/1024)}k bytes")

#下载完lib之后顺便测试一下sdk，如果上一层目录的client_config和本目录的bcos3_sdk_config.ini里的信息配置是对的，
# 那么应该可以打印出版本信息，否则会抛异常
print(" --- download DONE. make sure config file (etc: client_config.py and bcos3_sdk_config.ini) has setup right.")
print(" --- checking sdk :")
os.chdir("../")
client =  Bcos3Client()
print(client.getinfo())
