from enum import Enum
from typing import Any, Callable, Dict, Iterable, Tuple
from _socket import *
from socket import socket
_LOCALHOST    = '127.0.0.1'
_LOCALHOST_V6 = '::1'
try: from socket import _LOCALHOST, _LOCALHOST_V6
except: pass


class MsgType(Enum):
    Func = 'Call a function'
    AsyncFunc = 'Call a asynchronous function'
    Method = 'Call a method'
    AsyncMethod = 'Call a asynchronous method'
    Class = 'Instantiate a class'
    Return = 'Return value'


def build_socket(family=None, type=SOCK_STREAM, proto=0) -> Tuple[socket, str, str]:
    '''
    建立socket
    '''
    if family is None:
        try:
            family = AF_UNIX
        except NameError:
            family = AF_INET
    if family == AF_INET:
        host = _LOCALHOST
    elif family == AF_INET6:
        host = _LOCALHOST_V6
    else:
        raise ValueError("Only AF_INET and AF_INET6 socket address families ")

    lsock = socket(family, type, proto)
    
    lsock.bind((host, 0))

    # On IPv6, ignore flow_info and scope_id
    addr, port = lsock.getsockname()[:2]
    return lsock, addr, port


