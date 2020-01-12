FROM python:3.7-alpine

LABEL 99kies 1290017556@qq.com https://github.com/99kies

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && \
    apk update && \
    apk add --no-cache git gcc g++ python python-dev py-pip mysql-dev openssl bash linux-headers libffi-dev openssl-dev curl wget && \
    bash && \
    cd ~ && mkdir -p fisco && cd fisco && \
    curl -Ls https://raw.githubusercontent.com/FISCO-BCOS/FISCO-BCOS/master/tools/get_buildchain.sh > get_buildchain.sh && chmod u+x get_buildchain.sh && \
    bash get_buildchain.sh && chmod u+x build_chain.sh && \
    bash build_chain.sh -l "127.0.0.1:4" -p 30300,20200,8545 && \
    cd / && \
    git clone https://github.com/FISCO-BCOS/python-sdk && \
    cd python-sdk && \
    pip install -r requirements.txt --user && \
    bash init_env.sh -i && \
    cp ~/fisco/nodes/127.0.0.1/sdk/* bin/ && \
    ln -s /root/.local/bin/register-python-argcomplete /bin/register-python-argcomplete && \
    echo "eval \"\$(register-python-argcomplete ./console.py)\"" >> ~/.bashrc && \
    source ~/.bashrc && \
    rm /var/cache/apk/*

EXPOSE 20200 30300 8545

CMD ["bash"]