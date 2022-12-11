from enum import Enum
from typing import Any, Callable, Dict, Iterable, Tuple
from _socket import *
from socket import socket, SOL_SOCKET, SO_RCVBUF, SO_SNDBUF

_LOCALHOST    = '127.0.0.1'
_LOCALHOST_V6 = '::1'
try: from socket import _LOCALHOST, _LOCALHOST_V6
except: pass

from uuid import uuid1, uuid4
from pathlib import Path

class MsgType(Enum):
    Func = 'Call a function'
    AsyncFunc = 'Call a asynchronous function'
    Method = 'Call a method'
    AsyncMethod = 'Call a asynchronous method'
    Class = 'Instantiate a class'
    Return = 'Return value'
    Init = "Init"


def build_socket(family=None, type=SOCK_STREAM, proto=0, uds_root=...) -> Tuple[socket, str, str]:
    '''
    建立socket
    '''
    if family is None:
        try:
            global AF_UNIX
            family = AF_UNIX
            _AF_UNIX = AF_UNIX
        except NameError:
            family = AF_INET
            _AF_UNIX = None
    lsock = socket(family, type, proto)
    if family in (AF_INET, AF_INET6):    
        if family == AF_INET:
            host = _LOCALHOST
        elif family == AF_INET6:
            host = _LOCALHOST_V6
        lsock.bind((host, 0))
        # On IPv6, ignore flow_info and scope_id
        host, port = lsock.getsockname()[:2]
        addr = (host, port)
    elif family == _AF_UNIX:
        if uds_root is Ellipsis:
            uds_root = './'
        if uds_root is not None:
            uds_root = Path(uds_root)
            addr = str(uds_root/f'{hash((uuid1(), uuid4()))}.sock')
            lsock.bind(addr)
            addr = lsock.getsockname()
            addr = str(Path(addr).absolute())
        else:
            addr = None
    else:
        raise TypeError('family type error!')

    return lsock, addr
