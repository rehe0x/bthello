#!/usr/bin/env python3
# encoding: utf-8

from dht import DHTServer
#from model.init import database_initialize
from common.database import RedisClients

if __name__ == "__main__":
    #RedisClients.set_keyinfo("4d8ea85ce90562156ebd7330bd631eaa7b6825f0","1111111")
    dht = DHTServer()
    dht.start()
    dht.auto_send_find_node()
