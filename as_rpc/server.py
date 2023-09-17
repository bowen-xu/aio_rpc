from .base import AioRpcBase, _asynchronify
from .utils import build_socket, MsgType
from aiosock import AioSock
import asyncio
import inspect
import json
import os
from typing import Callable, Dict, Tuple, Any, Coroutine, Awaitable
from pathlib import Path
from socket import AddressFamily, socket, SOL_SOCKET, SO_RCVBUF, SO_SNDBUF
from .handler import get_handler
AF_UNIX = None
try:
    from socket import AF_UNIX
except:
    pass


def rpc(instance: 'AioRpcBase', name):
    def my_decorator(func: 'Callable|Awaitable'):
        if inspect.iscoroutinefunction(func):
            instance.add_async(func, name)
        elif inspect.isfunction(func):
            instance.add(func, name)
        elif inspect.isclass(func):
            instance.add_class(func, name)
        return func

    return my_decorator


class AioRpcServer(AioRpcBase):

    def __init__(self, root='cache/io_process/', name='IOP0', buff=65535, on_handshake: Callable[[int, str], None] = None) -> None:
        ''''''
        super().__init__()
        self.reset(root, name)

        self.clients: Dict[int, AioSock] = {}
        self.msg_handlers[MsgType.Init] = self._handle_msg__Init
        RpcServerObject.server = self

        self.buff = buff

        self.on_handshake = on_handshake

    def init(self):
        try:
            loop = asyncio.get_event_loop()
        except:
            asyncio.set_event_loop(asyncio.SelectorEventLoop())
            loop = asyncio.get_event_loop()
        self.loop = loop
        print('IO Process'.center(50, '='))

        try:
            # delete the old socket file
            filename = self.root/(self.name+'.json')
            if filename.exists():
                with open(filename, 'r') as f:
                    info = json.load(f)
                    info = info[self.name]
                addr = info['addr']
                family = info['family']
                family = AddressFamily[family]
                if family is AF_UNIX and Path(addr).exists():
                    os.unlink(addr)
        except:
            pass

        lsock, addr = build_socket(uds_root=self.root)
        lsock.setsockopt(SOL_SOCKET, SO_RCVBUF, self.buff)
        lsock.setsockopt(SOL_SOCKET, SO_SNDBUF, self.buff)

        print('lsock', lsock)
        loop.create_task(self._start_listening(lsock, self._on_acception))
        filename = self.root/(self.name+'.json')
        with open(filename, 'w') as f:
            json.dump({
                self.name: {
                    'addr': addr,
                    'family': lsock.family.name
                }
            }, f)
        print(f'Server [{self.name}]: {addr}')
        print('IO Process'.center(50, '-'))

        self.init_ok.set()

    def _on_acception(self, ssock: AioSock):
        ssock.init((self._on_sock_recv, ssock))

    async def _start_listening(self, lsock: socket, callback_accept: 'Callable|Coroutine' = None):
        ''''''
        print('start listening')
        lsock.listen()
        lsock.setblocking(False)

        loop = asyncio.get_event_loop()

        while True:
            ssock, _ = await loop.sock_accept(lsock)
            print('sscok', ssock)
            ssock = AioSock(ssock, 4)

            if callback_accept is not None:
                if inspect.iscoroutinefunction(callback_accept):
                    loop.create_task(callback_accept(ssock))
                elif inspect.isfunction(callback_accept) or inspect.ismethod(callback_accept):
                    loop.call_soon(callback_accept, ssock)
                else:
                    raise TypeError('callback_accept: error type')

    def _handle_msg__Init(self, data, ssock: AioSock):
        ''''''
        _, pack_id, client_id, mark = data
        self.clients[client_id] = ssock
        self.objs[client_id] = ssock
        ret = self.id
        if pack_id is not None:
            ssock.write((MsgType.Return, pack_id, (ret, None)))
        if self.on_handshake is not None:
            self.on_handshake(client_id, mark)

    def call_func(self, client_id, name_func, callback, *args):
        ''''''
        ssock = self.clients.get(client_id)
        if ssock is None:
            return
        pack_id = self._new_pack_id(callback)
        ssock.write((MsgType.Func, pack_id, name_func, args))

    @_asynchronify(call_func, 2)
    async def async_call_func(self, client_id, name_func, *args):
        ''''''

    def call_async_func(self, client_id, name_func, callback, *args):
        ''''''
        ssock = self.clients.get(client_id)
        if ssock is None:
            return
        pack_id = self._new_pack_id(callback)
        ssock.write((MsgType.AsyncFunc, pack_id, name_func, args))

    @_asynchronify(call_async_func, 2)
    async def async_call_async_func(self, client_id, name_func, *args):
        ''''''

    def call_method(self, client_id, name_self, name_method, callback, *args):
        ''''''
        ssock = self.clients.get(client_id)
        if ssock is None:
            return
        pack_id = self._new_pack_id(callback)
        ssock.write((MsgType.Method, pack_id, name_self, name_method, args))

    @_asynchronify(call_method, 3)
    async def async_call_method(self, client_id, name_self, name_method, *args):
        ''''''

    def call_async_method(self, client_id, name_self, name_method, callback, *args):
        ''''''
        ssock = self.clients.get(client_id)
        if ssock is None:
            return
        pack_id = self._new_pack_id(callback)
        ssock.write((MsgType.AsyncMethod, pack_id,
                    name_self, name_method, args))

    @_asynchronify(call_async_method, 3)
    async def async_call_async_method(self, client_id, name_self, name_method, *args):
        ''''''

    def instantiate(self, client_id, name_class, callback, *args):
        '''
        create a new instance, e.g., a instance of a class, a number, and so on.
        '''
        ssock = self.clients.get(client_id)
        if ssock is None:
            return
        pack_id = self._new_pack_id(callback)
        ssock.write((MsgType.Class, pack_id, name_class, args))

    @_asynchronify(instantiate, 2)
    async def async_instantiate(self, client_id, name_class, *args) -> int:
        '''
        create a new instance, e.g., a instance of a class, a number, and so on.
        '''

    def get_progress(self, client_id, name, callback):
        '''
        get remote progress
        '''
        self.call_method(client_id, client_id, get_handler(
            AioRpcBase._get_local_progress), callback, name)

    async def add_progress(self, client_id, name):
        '''
        add remote progress
        '''
        return await self.async_call_method(client_id, client_id, get_handler(AioRpcBase._add_local_progress), name)

    def run(self) -> None:
        ''''''
        self.init()
        loop = asyncio.get_event_loop()
        loop.run_forever()


class RpcServerObject:
    server: AioRpcServer = None

    def __init__(self, _id):
        self._id = _id

    @classmethod
    def get_obj(cls, _id):
        ''''''
        if cls.server is None:
            return None
        else:
            return cls.server.objs.get(_id)

    def __reduce__(self):
        return (RpcServerObject.get_obj, (self._id, ))


if __name__ == '__main__':
    root = Path('../cache/io_process/')
    root.mkdir(parents=True, exist_ok=True)
    print(f'cache root: {str(root)}')
    server = AioRpcServer(root, 'IOP0')
    server.run()
