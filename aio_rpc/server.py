import os
from typing import Callable, Dict, Tuple, Any, Coroutine, Awaitable
from pathlib import Path
from socket import AddressFamily, socket

AF_UNIX = None
try:from socket import AF_UNIX
except: pass

import json
import inspect

import asyncio

from aiosock import AioSock
from .utils import build_socket, MsgType
from .base import AioRpcBase
from uuid import uuid1, uuid4


def rpc(instance: 'AioRpcServer', name):
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
    
    def __init__(self, root='cache/io_process/', name='IOP0') -> None:
        ''''''
        super().__init__()
        self.root = Path(root)
        self.name = name
        self.root.mkdir(parents=True, exist_ok=True)

        self.msg_handlers = {
            MsgType.Func: self._handle_msg__Func,
            MsgType.AsyncFunc: self._handle_msg__AsyncFunc,
            MsgType.Method: self._handle_msg__Method,
            MsgType.AsyncMethod: self._handle_msg__AsyncMethod,
            MsgType.Class: self._handle_msg__Class
        }


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


    def add(self, func, name):
        ''''''
        self.funcs[name] = func
    

    def add_async(self, func_coro, name):
        ''''''
        self.func_async[name] = func_coro


    def add_class(self, cls, name):
        ''''''
        self.classes[name] = cls

    def _on_acception(self, ssock: AioSock):
        ssock.init((self._on_sock_recv, ssock))


    def _handle_msg__Func(self, data, ssock: AioSock):
        _, pack_id, name, args = data
        func = self.funcs.get(name, None)
        ret = func(*args)
        if pack_id is not None:
            ssock.write((MsgType.Return, pack_id, ret))

    def _handle_msg__AsyncFunc(self, data, ssock: AioSock):
        _, pack_id, name, args = data
        func_async = self.func_async.get(name, None)
        async def wrapper(func, args):
            ret = await func(*args)
            if pack_id is not None:
                ssock.write((MsgType.Return, pack_id, ret))
        self.loop.create_task(wrapper(func_async, args))

    def _handle_msg__Method(self, data, ssock: AioSock):
        _, pack_id, name_obj, name_method, args = data
        method = self.funcs.get(name_method, None)
        obj = self.objs.get(name_obj, None)
        ret = method(obj, *args)
        if pack_id is not None:
            ssock.write((MsgType.Return, pack_id, ret))

    def _handle_msg__AsyncMethod(self, data, ssock: AioSock):
        _, pack_id, name_obj, name_method, args = data
        method_async = self.func_async.get(name_method, None)
        obj = self.objs.get(name_obj, None)
        async def wrapper(obj, func, args):
            ret = await func(obj, *args)
            if pack_id is not None:
                ssock.write((MsgType.Return, pack_id, ret))
        self.loop.create_task(wrapper(obj, method_async, args))
    
    def _handle_msg__Class(self, data, ssock: AioSock):
        _, pack_id, name_class, args = data
        cls = self.classes.get(name_class, None)
        obj = cls(*args)
        obj_id = hash((uuid1(), uuid4()))
        self.objs[obj_id] = obj

        if pack_id is not None:
            ssock.write((MsgType.Return, pack_id, obj_id))

    def _on_sock_recv(self, data: Tuple[MsgType, int, Any, Tuple], ssock: AioSock):
        ''''''
        msg_type = data[0]
        msg_handler = self.msg_handlers.get(msg_type, None)
        if msg_handler is not None:
            msg_handler(data, ssock)
            

    async def _start_listening(self, lsock: socket, callback_accept: 'Callable|Coroutine'=None):
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
                    raise TypeError('callback_accept类型错误')

    def run(self) -> None:
        ''''''
        self.init()
        loop = asyncio.get_event_loop()
        loop.run_forever()


if __name__ == '__main__':
    root = Path('cache/io_process/')
    root.mkdir(parents=True, exist_ok=True)
    print(f'cache root: {str(root)}')
    server = AioRpcServer(root, 'IOP0')
    server.run()