FROM python:3.7-alpine

LABEL maintainer 99kies 1290017556@qq.com https://github.com/99kies

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk update && \
    apk add --no-cache git gcc g++ python python-dev py-pip mysql-dev linux-headers libffi-dev openssl-dev && \
    git clone https://github.com/FISCO-BCOS/python-sdk && \
    cd python-sdk && \
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    sh init_env.sh -i

EXPOSE 20200

CMD ["sh"]
