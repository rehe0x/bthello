FROM ubuntu:16.04

MAINTAINER wuyongchao

ENV MONGO_HOST      localhost
ENV MONGO_PORT      27017
ENV DOWNLOAD_THREAD 1000
ENV MAX_NODE_SIZE   500

WORKDIR /opt/spider

COPY . /opt/spider

RUN apt-get update
RUN apt-get install -y python3-pip python3-dev

RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

CMD ["python3", "run.py"]
