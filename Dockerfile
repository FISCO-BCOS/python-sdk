FROM python:3.7-alpine

LABEL 99kies 1290017556@qq.com https://github.com/99kies

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk update && \
    apk add --no-cache git gcc g++ python python-dev py-pip mysql-dev openssl bash linux-headers libffi-dev openssl-dev curl wget&& \
    bash && \
    cd ~ && mkdir -p fisco && cd fisco && \
    curl -Ls https://github.com/FISCO-BCOS/FISCO-BCOS/releases/download/v2.1.0/build_chain.sh > build_chain.sh && chmod u+x build_chain.sh && \
    bash build_chain.sh -l "127.0.0.1:4" -p 30300,20200,8545 && \
    bash nodes/127.0.0.1/start_all.sh && \
    cd / && \
    git clone https://github.com/FISCO-BCOS/python-sdk && \
    cd python-sdk && \
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    bash init_env.sh -i && \
    cp ~/fisco/nodes/127.0.0.1/sdk/* bin/

EXPOSE 20200 30300 8545

CMD ["bash"]
