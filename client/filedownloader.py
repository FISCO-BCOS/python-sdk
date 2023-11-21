import requests
from tqdm import tqdm




def download_file(url, local_path,proxies=None):
    response = requests.get(url,proxies=proxies)
    # 检查请求是否成功
    if response.status_code == 200:
        with open(local_path, 'wb') as file:
            file.write(response.content)
        print(f"File download to ：{local_path}")
    else:
        print(f"File download FAIL,status ：{response.status_code}")


def download_file_with_progress(url, local_path,proxies=None):
    response = requests.get(url, stream=True,proxies=proxies)
    
    # 获取文件大小（以字节为单位）
    file_size = int(response.headers.get('Content-Length', 0))
    
    # 设置进度条
    progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)
    
    # 写入文件
    with open(local_path, 'wb') as file:
        for data in response.iter_content(chunk_size=1024):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    print(f"File download to ：{local_path}")




'''
# 例子：下载图片
url = 'https://example.com/image.jpg'
local_path = 'path/to/save/image.jpg'

download_file(url, local_path)



# 例子：下载图片
url = 'https://example.com/image.jpg'
local_path = 'path/to/save/image.jpg'

download_file_with_progress(url, local_path)
'''
