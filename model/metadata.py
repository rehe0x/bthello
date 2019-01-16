#!/usr/bin/env python3
# encoding: utf-8

from time import time
from mongoengine import *
from common.filetype import get_file_type


class FileModel(EmbeddedDocument):
    n = StringField(default='', required=True)
    l = IntField(default=0, required=True)


class MetadataModel(Document):
    """
    metadata的数据结构
    _id: 以infohash替代mongodb自动生成的id
    n: 资源名称
    d: 资源创建时间
    l: 所有文件总大小
    s: 文件数量
    e: 是否启用，如某些文件不合法，可以通过设置此值来禁用，0表示禁用，1表示启用
    f: 资源所包含文件的详细信息列表，元素为包含文件名称和大小的字典
    m: 资源上次被下载的时间
    c: 资源热度
    """
    _id = StringField(default='', required=True)
    n = StringField(default='', required=True)
    d = IntField(default=0, required=True)
    l = IntField(default=0, required=True)
    s = IntField(default=0, required=True)
    e = IntField(default=1, required=True)
    f = ListField(EmbeddedDocumentField(FileModel))
    t = IntField(default=0, required=True)
    m = IntField(default=0)
    c = IntField(default=0)

    meta = {
        'collection': 'hashset',
        'db_alias': 'dht'
    }


def save_metadata(metadata, h):
    utf8_enable = False
    files = []
    # noinspection PyBroadException
    try:
        bare_name = metadata.get('name')
    except KeyError:
        bare_name = metadata.get('name.utf-8')
        utf8_enable = True
    except Exception:
        return
    if 'files' in metadata:
        for x in metadata.get('files'):
            files.append({'n': '/'.join(x.get('path.utf-8' if utf8_enable else 'path')),
                          'l': x.get('length')})
    else:
        files.append({'n': bare_name,
                      'l': metadata.get('length')})
    file_model = [FileModel(n=file.get('n'), l=file.get('l')) for file in files]
    MetadataModel.objects(_id=h).modify(set_on_insert___id=h,
                                        set_on_insert__n=bare_name,
                                        set_on_insert__d=int(time()),
                                        set_on_insert__l=sum(map(lambda y: y.get('l'), files)),
                                        set_on_insert__s=len(files),
                                        set_on_insert__e=1,
                                        set_on_insert__f=file_model,
                                        set_on_insert__t=get_file_type(files),
                                        set__m=int(time()),
                                        inc__c=1,
                                        upsert=True,
                                        new=True)
