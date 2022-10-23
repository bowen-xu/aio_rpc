import asyncio
from enum import Enum
from multiprocessing import Process
import os
import pickle
from time import sleep, time
from typing import Any, Callable, Dict, Iterable, Tuple, Type
import aiosock
from pathlib import Path
from _socket import *
from socket import socket

import inspect
_LOCALHOST    = '127.0.0.1'
_LOCALHOST_V6 = '::1'
try: from socket import _LOCALHOST, _LOCALHOST_V6
except: pass
import json
from typing import Coroutine

import aiosock
from aiosock import AioSock
from threading import Thread


class MsgType(Enum):
    Call = 'Call a function'
    Coro = 'Call a coroutine'
    Retn = 'Return value'


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


