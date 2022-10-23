
import asyncio
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
from .utils import MsgType, build_socket
# from aio_zmq_rpc import rpc


def rpc(instance: 'AioRpcServer', name):
    def my_decorator(func):
        instance.add(func, name)
        return func

    return my_decorator


class AioRpcServer(Thread):
    
    def __init__(self, root=Path('cache/io_process/'), name='IOP0') -> None:
        ''''''
        super().__init__()
        self.root = root
        self.name = name
        # self.callback_accept = callback_accept

        self.funcs = {}
        self.func_coros = {}


    def on_acception(self, ssock: AioSock):
        ssock.init((self._on_sock_recv, ssock))


    def _on_sock_recv(self, data: Tuple[MsgType, int, Any, Tuple], ssock: AioSock):
        ''''''
        msg_type, pack_id, name, args = data
        if msg_type is MsgType.Call:
            func = self.funcs.get(name, None)
            ret = func(*args)
            if pack_id is not None:
                ssock.write((MsgType.Retn, pack_id, ret))
                # print('write to client')


    
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
            self.ssock = ssock
            
            if callback_accept is not None:
                if inspect.iscoroutinefunction(callback_accept):
                    loop.create_task(callback_accept(ssock))
                elif inspect.isfunction(callback_accept) or inspect.ismethod(callback_accept):
                    loop.call_soon(callback_accept, ssock)
                else:
                    raise TypeError('callback_accept类型错误')


    def add(self, func, name):
        ''''''
        self.funcs[name] = func
    

    def add_async(self, func_coro, name):
        ''''''
        self.func_coros[name] = func_coro


    def run(self) -> None:
        ''''''
        # loop = asyncio.new_event_loop()
        asyncio.set_event_loop(asyncio.SelectorEventLoop())

        print('IO Process'.center(50, '='))
        
        loop = asyncio.get_event_loop()
        lsock, addr, port = build_socket()
        print('lsock', lsock)
        loop.create_task(self._start_listening(lsock, self.on_acception))
        filename = self.root/'AioRpcServer.json'
        with open(filename, 'w') as f:
            json.dump({
                self.name: {
                    'addr': addr,
                    'port': port
                }
            }, f)
        print(f'Server [{self.name}]: {addr}:{port}')
        print('IO Process'.center(50, '-'))
        loop.run_forever()

        os.remove(filename)


if __name__ == '__main__':
    root = Path('cache/io_process/')
    root.mkdir(parents=True, exist_ok=True)
    print(f'cache root: {str(root)}')
    server = AioRpcServer(root, 'IOP0')
    server.run()