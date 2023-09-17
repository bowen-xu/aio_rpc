from asyncio import Event
from socket import AF_INET, AF_INET6, AddressFamily, SOL_SOCKET, SO_RCVBUF, SO_SNDBUF
from typing import Callable, Dict, Tuple
from pathlib import Path
import uuid

import json

from aiosock import AioSock
from .utils import build_socket, MsgType
from .base import AioRpcBase, _asynchronify
from .progress import Progress
from collections import defaultdict
from .handler import get_handler

class AioRpcClient(AioRpcBase):
    csock: AioSock = None

    def __init__(self, root='cache/io_process/', name='IOP0', buff=65535, mark=None) -> None:
        ''''''
        super().__init__()
        self.reset(root, name)
        self.server_id = None
        self.buff = buff
        self.mark = mark


    def init(self, callback: Callable = None):
        filename = self.root/(self.name+'.json')
        with open(filename, 'r') as f:
            info = json.load(f)
            info = info[self.name]
        addr = info['addr']
        family = info['family']
        family = AddressFamily[family]
        if family in (AF_INET, AF_INET6):
            addr = tuple(addr)
        else:
            addr = str(addr)

        csock, *_ = build_socket(uds_root=None)
        csock.setblocking(True)
        csock.setsockopt(SOL_SOCKET, SO_RCVBUF, self.buff)
        csock.setsockopt(SOL_SOCKET, SO_SNDBUF, self.buff)

        print('connecting...')
        csock.connect(addr)
        print('csock', csock)
        csock = AioSock(csock, 4)
        self.csock = csock

        csock.init((self._on_sock_recv, csock))
        self._handshake()
        if callback is not None:
            callback()

    def _handshake(self):
        ''''''
        def callback(_id):
            ''''''
            self.server_id, err = _id
            if err:
                raise Exception(
                    "Handshake Error: Client RPC cannot connect to Server RPC correctly.")
            self.init_ok.set()
        pack_id = self._new_pack_id(callback)
        self.csock.write((MsgType.Init, pack_id, self.id, self.mark))

    def call_func(self, name_func, callback, *args):
        ''''''
        pack_id = self._new_pack_id(callback)

        self.csock.write((MsgType.Func, pack_id, name_func, args))

    @_asynchronify(call_func, 1)
    async def async_call_func(self, name_func, *args):
        ''''''

    def call_async_func(self, name_func, callback, *args):
        ''''''
        pack_id = self._new_pack_id(callback)
        self.csock.write((MsgType.AsyncFunc, pack_id, name_func, args))

    @_asynchronify(call_async_func, 1)
    async def async_call_async_func(self, name_func, *args):
        ''''''

    def call_method(self, name_self, name_method, callback, *args):
        ''''''
        pack_id = self._new_pack_id(callback)
        self.csock.write(
            (MsgType.Method, pack_id, name_self, name_method, args))

    @_asynchronify(call_method, 2)
    async def async_call_method(self, name_self, name_method, *args):
        ''''''

    def call_async_method(self, name_self, name_method, callback, *args):
        ''''''
        pack_id = self._new_pack_id(callback)
        self.csock.write((MsgType.AsyncMethod, pack_id,
                         name_self, name_method, args))

    @_asynchronify(call_async_method, 2)
    async def async_call_async_method(self, name_self, name_method, *args):
        ''''''

    def instantiate(self, name_class, callback, *args):
        '''
        create a new instance, e.g., a instance of a class, a number, and so on.
        '''
        pack_id = self._new_pack_id(callback)
        self.csock.write((MsgType.Class, pack_id, name_class, args))

    @_asynchronify(instantiate, 1)
    async def async_instantiate(self, name_class, *args) -> int:
        '''
        create a new instance, e.g., a instance of a class, a number, and so on.
        '''

    def get_progress(self, name, callback):
        '''
        get remote progress
        '''
        self.call_method(self.server_id, get_handler(AioRpcBase._get_local_progress), callback, name)

    def add_progress(self, name, callback):
        '''
        add remote progress
        '''
        self.call_method(self.server_id, get_handler(AioRpcBase._add_local_progress), callback, name)


