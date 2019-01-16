#!/usr/bin/env python
# coding=utf-8

import redis
from .utils import get_logger
from config import Config

class RedisClient:

    def __init__(
        self, host=Config.REDIS_HOST, port=Config.REDIS_PORT, password=Config.REDIS_PASSWORD
    ):
        conn_pool = redis.ConnectionPool(
            host=host,
            port=port,
            password=password,
            max_connections=Config.REDIS_MAX_CONNECTION,
        )
        self.redis = redis.Redis(connection_pool=conn_pool)
        self.logger = get_logger("logger_redis")
        
    def add_magnet(self, magnet):
        """
        新增磁力链接
        """
        self.redis.sadd(Config.REDIS_KEY, magnet)

    def add_peer(self,infohash,address):
        """
        新增磁力peer信息
        """    
        self.redis.sadd('peer',str(infohash)+':'+address[0]+':'+str(address[1]))
        # if (self.redis.exists(infohash) == False):
        #     self.redis.sadd('peer',str(infohash)+':'+address[0]+':'+str(address[1]))
        # else:
        #     self.logger.info("该种子已存在:infohash>{0}".format(infohash))

    def set_keyinfo(self,infohash,metadata):
        """
        """    
        self.redis.set(infohash,metadata)
        print(str(infohash))


    def get_magnets(self, count=128):
        """
        返回指定数量的磁力链接
        """
        return self.redis.srandmember(Config.REDIS_KEY, count)

    def get_redis_byKey(self,key,count):
        """
        返回指定数量的磁力链接
        """
        return self.redis.srandmember(key, count)    

RedisClients = RedisClient()
