from typing import Callable, Dict, Tuple
from pathlib import Path
import uuid

import json

from aiosock import AioSock
from .utils import build_socket, MsgType
from .node import AioRpcNode


class AioRpcClient(AioRpcNode):
    csock: AioSock = None

    def __init__(self, root=Path('cache/io_process/'), name='IOP0') -> None:
        ''''''
        super().__init__()
        self.root = root
        self.name = name
        self.callbacks: Dict[int, Callable] = {}
        # self.callback_accept = callback_accept


    def init(self):
        filename = self.root/(self.name+'.json')
        with open(filename, 'r') as f:
            info = json.load(f)
            info = info[self.name]
        addr, port = info['addr'], info['port']
        csock, *_ = build_socket()
        csock.setblocking(True)

        print('connecting...')
        csock.connect((addr, port))
        print('csock', csock)
        csock = AioSock(csock, 4)
        self.csock = csock

        csock.init(self._on_sock_recv)


    def call(self, name_func, callback, *args):
        ''''''
        if callback is not None:
            pack_id = hash((uuid.uuid1(), uuid.uuid4()))
            self.callbacks[pack_id] = callback
        else: 
            pack_id = None
        self.csock.write((MsgType.Call, pack_id, name_func, args))


    async def async_call(self, name_func, *args):
        ''''''


    def _on_sock_recv(self, data: Tuple[MsgType, int, Tuple]):
        ''''''
        msg_type = data[0]
        if msg_type is MsgType.Retn:
            _, pack_id, ret = data
            callback = self.callbacks[pack_id]
            callback(ret)

