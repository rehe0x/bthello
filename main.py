#!/usr/bin/env python3
# encoding: utf-8

from dht import DHTServer
from common.database import RedisClients
from common.utils import get_logger
from config import Config

logger = get_logger("logger_dht_main")

if __name__ == "__main__":
    dht = DHTServer()
    dht.start()
    dht.auto_send_find_node()
    logger.info("dht running successful ! >>>> {0}:{1}".format(Config.BIND_IP,Config.BIND_PORT))