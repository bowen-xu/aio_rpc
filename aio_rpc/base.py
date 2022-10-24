
from multiprocessing import Process
import asyncio
from typing import Callable, Dict
from uuid import uuid1, uuid4

class AioRpcBase(Process):
    def __init__(self) -> None:
        super().__init__()
        
        self.funcs = {}
        self.func_async = {}

        self.classes = {}
        self.objs = {}

        self.loop: asyncio.BaseEventLoop = None

        self.callbacks: Dict[int, Callable] = {}


    def init(self):
        raise NotImplementedError()


    def run(self) -> None:
        ''''''
        self.init()
        loop = asyncio.get_event_loop()
        loop.run_forever()

    
    def _get_pack_id(self, callback):
        if callback is not None:
            pack_id = hash((uuid1(), uuid4()))
            self.callbacks[pack_id] = callback
        else: 
            pack_id = None
        return pack_id