#!/usr/bin/env python3
# encoding: utf-8

import socket
from multiprocessing import Process
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from collections import deque
from common.bencode import bencode, bdecode
from common.utils import *
from config import Config
from common.metadata import download_metadata
from common.database import RedisClient

logger = get_logger("logger_dht_main")

class KNode(object):
    def __init__(self, nid, ip, port):
        self.nid = nid
        self.ip = ip
        self.port = port


class DHT(Thread):
    def __init__(self,bind_ip,bind_port):
        Thread.__init__(self)
        self.ufd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.ufd.bind((bind_ip, bind_port))

    def send_krpc(self, msg, address):
        # noinspection PyBroadException
        try:
            self.ufd.sendto(bencode(msg), address)
        except Exception:
            pass


class DHTClient(DHT):
    def __init__(self,bind_ip,bind_port):
        DHT.__init__(self,bind_ip,bind_port)
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self.setDaemon(True)
        self.nid = random_id()
        self.nodes = deque(maxlen=Config.MAX_NODE_SIZE)

    def send_find_node(self, address, nid=None):
        nid = get_neighbor(nid, self.nid) if nid else self.nid
        tid = entropy(2)  # TransactionID长度为2
        msg = {
            't': tid,
            'y': 'q',
            'q': 'find_node',
            'a': {
                'id': nid,
                'target': random_id()
            }
        }
        self.send_krpc(msg, address)

    def join_dht(self):
        for address in Config.BOOTSTRAP_NODES:
            self.send_find_node(address)

    def rejoin_dht(self):
        if len(self.nodes) == 0:
            self.join_dht()
        timer(Config.REJOIN_DHT_INTERVAL, self.rejoin_dht)

    def auto_send_find_node(self):
        while True:
            try:
                node = self.nodes.popleft()
                self.send_find_node((node.ip, node.port), node.nid)
            except IndexError:
                pass
            sleep(1.0 / Config.MAX_NODE_SIZE)

    def process_find_node_response(self, msg):
        nodes = decode_nodes(msg['r']['nodes'])
        for node in nodes:
            (nid, ip, port) = node
            if len(nid) != 20:
                continue
            if ip == self.bind_ip:
                continue
            n = KNode(nid, ip, port)
            self.nodes.append(n)


class DHTServer(DHTClient):
    def __init__(self,bind_ip, bind_port, process_id):
        DHTClient.__init__(self,bind_ip,bind_port)
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self.process_id = process_id
        self.pool = ThreadPoolExecutor(Config.DOWNLOAD_THREAD)
        self.process_request_actions = {
            'get_peers': self.on_get_peers_request,
            'announce_peer': self.on_announce_peer_request,
        }
        self.ufd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.ufd.bind((self.bind_ip, self.bind_port))
        timer(Config.REJOIN_DHT_INTERVAL, self.rejoin_dht)
    def run(self):
        self.rejoin_dht()
        while True:
            # noinspection PyBroadException
            try:
                (data, address) = self.ufd.recvfrom(65536)
                msg = bdecode(data)
                self.on_message(msg, address)
            except Exception:
                pass

    def on_message(self, msg, address):
        try:
            if msg['y'] == 'r':
                if 'nodes' in msg['r']:
                    self.process_find_node_response(msg)
            elif msg['y'] == 'q':
                try:
                    self.process_request_actions[msg['q']](msg, address)
                except KeyError:
                    self.play_dead(msg, address)
        except KeyError:
            pass

    def on_get_peers_request(self, msg, address):
        try:
            h = msg['a']['info_hash']
            tid = msg['t']
            token = h[:2]
            msg = {
                't': tid,
                'y': 'r',
                'r': {
                    'id': get_neighbor(h, self.nid),
                    'nodes': '',
                    'token': token
                }
            }
            self.send_krpc(msg, address)
        except KeyError:
            pass

    def on_announce_peer_request(self, msg, address):
        # noinspection PyBroadException
        try:
            h = msg['a']['info_hash']
            token = msg['a']['token']
            if h[:2] == token:
                if 'implied_port ' in msg['a'] and msg['a']['implied_port '] != 0:
                    port = address[1]
                else:
                    port = msg['a']['port']
                self.pool.submit(download_metadata, (address[0], port), h, self.process_id)
        except Exception:
            return
        finally:
            self.ok(msg, address)

    def play_dead(self, msg, address):
        try:
            tid = msg['t']
            msg = {
                't': tid,
                'y': 'e',
                'e': [202, 'Server Error']
            }
            self.send_krpc(msg, address)
        except KeyError:
            pass

    def ok(self, msg, address):
        try:
            tid = msg['t']
            nid = msg['a']['id']
            msg = {
                't': tid,
                'y': 'r',
                'r': {
                    'id': get_neighbor(nid, self.nid)
                }
            }
            self.send_krpc(msg, address)
        except KeyError:
            pass

def _start_thread(offset):
    """
    启动线程

    :param offset: 端口偏移值
    """
    logger.info("dht running successful ! {0} ->>>> {1}:{2}".format(offset,Config.BIND_IP,Config.BIND_PORT + offset))
    dht = DHTServer(Config.BIND_IP, Config.BIND_PORT + offset, offset)
    dht.start()
    dht.auto_send_find_node()
    # t = Thread(target=dht.auto_send_find_node)
    # t.start()
    # t.join()
    # dht.join()


def start_server():
    """
    多线程启动服务
    """
    processes = []
    for i in range(Config.MAX_PROCESSES):
        processes.append(Process(target=_start_thread, args=(i,)))

    for p in processes:
        p.start()

    for p in processes:
        p.join()
