# BTHello Python3 DHT磁力爬虫

## 简介

这是一个 magnet磁力连接爬虫，通过伪装成一个 DHT 节点，接收其他节点发过来的请求信息，提取相关的 magnet磁力链接。 然后实现BitTorrent BEP-9协议来获取种子文件信息，把文件信息存入redis。

### 地址

[bthello](https://github.com/xieh1995/bthello.git)  爬虫程序

[bthello-app](https://github.com/xieh1995/bthello-app.git) 入库程序&web搜索

### 技术栈

使用redis存储种子基本信息 infohash当key 避免了重复

使用elasticsearch为用户提供搜索功能

### 入库程序说明

入库程序会定时从redis获取数据同步到es  infohash作为es id 避免重复 如果id相同 es version+1 version值越大说明种子热度越高



# BTHello安装

### 说明

- 爬虫程序和入库&web搜索程序是两个工程  可以分开部署 根据自己的需求
- 比如有a b c 3台服务器分布部署 爬虫 入库 web搜索 

### 运行环境

- Python3.x
- redis4.x
- elasticsearch6.x

### 爬虫程序部署

```shell
git clone https://github.com/xieh1995/bthello.git
cd bthello

#修改redis配置
vi config.py

# redis 地址
REDIS_HOST = "你的redis ip"
# redis 端口
REDIS_PORT = 你的redis ip

#安装依赖包
pip3 install -r requirements.txt
#运行
python3 run.py

#后台运行
nohub python3 run.py &
#日志查看
tail -f nohub.out
```

运行成功 等待几分钟出现如下输出:

![1](https://xieh1995.github.io/bthello-app/doc/image-20190120153842915.png)

就说明已经在爬取了 同时可以看redis[0] 有无数据

![image-20190120155238627](https://xieh1995.github.io/bthello-app/doc/image-20190120155238627.png)



### 入库程序 & web搜索部署

```shell
git clone https://github.com/xieh1995/bthello-app.git
cd bthello-app

#修改redis es配置
vi config.py

# redis 地址
REDIS_HOST = "你的redis ip"
# redis 端口
REDIS_PORT = 你的redis ip

#elastics 索引名称
ELASTICS_INDEX_NAME = 'bt_metadata'
#elastics 索引类型
ELASTICS_INDEX_TYPE = 'doc'
# elastics 地址
ELASTICS_HOST = "你的es ip"
# elastics 端口
ELASTICS_PORT = 你的es 端口

#安装依赖包
pip3 install -r requirements.txt

#运行参数说明
-w		#启动web搜索
-m		#启动入库程序
-a		#同时启动web搜索 入库程序
-port	#web搜索端口 默认8000

#根据自己需求启动
python3 main.py -m
python3 main.py -w -port=80
python3 main.py -a -port=80
```

入库程序运行成功日志

![image-20190120154911906](https://xieh1995.github.io/bthello-app/doc/image-20190120154911906.png)



web搜索可以访问 ip:port 



# BTHello常见问题

### 好久有数据?

###### 1 - 20分钟内 服务器必须可外网访问 爬虫数据在redis[0]

### es好久才有数据?

正常情况只要启动了入库程序 2秒执行一次任务 马上就会用 前提是redis[0] 有数据   入库数据在redis[1] 也存了一份

# 有任何问题可以通过Issues提问



# TODO

- 完成web页面相关
- 优化多线程
- 优化入库程序避免重复入库



最后感谢[DHTSpider](https://github.com/ycwoo/DHTSpider)项目提供了爬虫协议实现
