from asyncio import Event
from socket import AF_INET, AF_INET6, AddressFamily
from typing import Callable, Dict, Tuple
from pathlib import Path
import uuid

import json

from aiosock import AioSock
from .utils import build_socket, MsgType
from .base import AioRpcBase

def _asynchronify(_call, pos_callback):
    ''''''
    def wrapper(_func):
        ''''''
        async def async_call(self, *args):
            event = Event()
            event.clear()
            obj_id = None
            def callback(_obj_id):
                ''''''
                nonlocal obj_id
                obj_id = _obj_id
                event.set()
            _call(self, *args[:pos_callback], callback, *args[pos_callback:])
            await event.wait()
            return obj_id
        return async_call
    return wrapper

class AioRpcClient(AioRpcBase):
    csock: AioSock = None

    def __init__(self, root='cache/io_process/', name='IOP0') -> None:
        ''''''
        super().__init__()
        self.root = Path(root)
        self.name = name
        # self.callback_accept = callback_accept
        self.root.mkdir(parents=True, exist_ok=True)

    def init(self):
        filename = self.root/(self.name+'.json')
        with open(filename, 'r') as f:
            info = json.load(f)
            info = info[self.name]
        addr = info['addr']
        family = info['family']
        family = AddressFamily[family]
        if family in (AF_INET, AF_INET6): addr = tuple(addr)
        else: addr = str(addr)
        
        csock, *_ = build_socket(uds_root=None)
        csock.setblocking(True)

        print('connecting...')
        csock.connect(addr)
        print('csock', csock)
        csock = AioSock(csock, 4)
        self.csock = csock

        csock.init(self._on_sock_recv)


    def call_func(self, name_func, callback, *args):
        ''''''
        pack_id = self._get_pack_id(callback)
        
        self.csock.write((MsgType.Func, pack_id, name_func, args))


    @_asynchronify(call_func, 1)
    async def async_call_func(self, name_func, *args):
        ''''''
        

    def call_async_func(self, name_func, callback, *args):
        ''''''
        pack_id = self._get_pack_id(callback)
        self.csock.write((MsgType.AsyncFunc, pack_id, name_func, args))


    @_asynchronify(call_async_func, 1)
    async def async_call_async_func(self, name_func, *args):
        ''''''

    
    def call_method(self, name_self, name_method, callback, *args):
        ''''''
        pack_id = self._get_pack_id(callback)
        self.csock.write((MsgType.Method, pack_id, name_self, name_method, args))


    @_asynchronify(call_method, 2)
    async def async_call_method(self, name_self, name_method, *args):
        ''''''


    def call_async_method(self, name_self, name_method, callback, *args):
        ''''''
        pack_id = self._get_pack_id(callback)
        self.csock.write((MsgType.AsyncMethod, pack_id, name_self, name_method, args))

    
    @_asynchronify(call_async_method, 2)
    async def async_call_async_method(self, name_self, name_method, *args):
        ''''''


    def instantiate(self, name_class, callback, *args):
        '''
        create a new instance, e.g., a instance of a class, a number, and so on.
        '''
        pack_id = self._get_pack_id(callback)
        self.csock.write((MsgType.Class, pack_id, name_class, args))


    @_asynchronify(instantiate, 1)
    async def async_instantiate(self, name_class, *args):
        '''
        create a new instance, e.g., a instance of a class, a number, and so on.
        '''



    def _on_sock_recv(self, data: Tuple[MsgType, int, Tuple]):
        ''''''
        msg_type = data[0]
        if msg_type is MsgType.Return:
            _, pack_id, ret = data
            callback = self.callbacks[pack_id]
            callback(ret)

