#!/usr/bin/env python3
# encoding: utf-8


def bencode(x):
    """
    :param x: 待编码的字典
    :return: 编码后的b编码
    """
    if isinstance(x, int):
        return 'i'.encode() + str(x).encode() + 'e'.encode()
    elif isinstance(x, str):
        x = x.encode('utf-8')
        return (str(len(x)) + ':').encode('ascii') + x
    elif isinstance(x, dict):
        keys = list(x.keys())
        keys.sort()
        end = 'd'.encode()
        for i in keys:
            if isinstance(i, str):
                end += bencode(i)
            else:
                raise TypeError('the kay must be str for dict.')
            end += bencode(x[i])
        end += 'e'.encode()
        return end
    elif isinstance(x, list):
        end = 'l'.encode()
        for i in x:
            end += bencode(i)
        end += 'e'.encode()
        return end
    else:
        # noinspection PyBroadException
        try:
            return (str(len(x)) + ':').encode('ascii') + x
        except Exception:
            raise TypeError('the arg data type is not support for bencode.')


__data = bytes()
__s = 0
__l = 0
__enc = False


def bdecode(x=None):
    """
    b编码解码
    :param x: 待解码的bytes
    :return: 解码后的object
    """
    global __data, __s, __l, __enc
    if not isinstance(x, bytes) and x is not None:
        raise TypeError('To decode the data type must be bytes.')
    elif x is not None:
        __s = 0
        __l = 0
        __data = x
        __l = len(__data)
    # 解码字典
    if __data[__s] == 100:
        __s += 1
        d = {}
        while __s < __l - 1:
            if __data[__s] not in range(48, 58):
                break
            key = bdecode()
            value = bdecode()
            d.update({key: value})
        __s += 1
        return d
    # 解码int
    elif __data[__s] == 105:
        temp = __s + 1
        key = ''
        while __data[temp] in range(48, 58):
            key += str(__data[temp] - 48)
            temp += 1
        __s += len(key) + 2
        return int(key)
    # 解码字符串
    elif __data[__s] in range(48, 58):
        temp = __s
        key = ''
        while __data[temp] in range(48, 58):
            key += str(__data[temp] - 48)
            temp += 1
        temp += 1
        key = __data[temp:temp + int(key)]
        __s = len(key) + temp
        if isinstance(__enc, list):
            for ii in __enc:
                # noinspection PyBroadException
                try:
                    return key.decode(ii)
                except Exception:
                    continue
        else:
            # noinspection PyBroadException
            try:
                return key.decode('utf-8')
            except Exception:
                # noinspection PyBroadException
                try:
                    return key.decode(__enc)
                except Exception:
                    return key
    # 解码列表
    elif __data[__s] == 108:
        li = []
        __s += 1
        while __s < __l:
            if __data[__s] == 101:
                __s += 1
                break
            li.append(bdecode())
        return li
