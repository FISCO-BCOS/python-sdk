FROM ubuntu:16.04

COPY sources.list /etc/apt/sources.list

RUN apt-get update && \
    apt install -y zlib1g-dev libffi6 libffi-dev wget git openssl gcc make && \
    wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz && \
    tar xzf Python-3.7.4.tgz && \
    cd /Python-3.7.4 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    apt install -y python3-pip python-pip && \
    cd / && \
    git clone https://github.com/FISCO-BCOS/python-sdk && \
    cd /python-sdk && \
    pip install --upgrade pip && \
    mkdir /root/.pip && \
    touch /root/.pip/pip.conf && \
    echo -e """[global] \nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple \n[install] \ntrusted-host=mirrors.aliyun.com""" > /root/.pip/pip.conf && \
    pip install -r requirements.txt && \
    bash init_env.sh -i

EXPOSE 20200
