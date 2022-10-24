
from multiprocessing import Process
import asyncio

class AioRpcBase(Process):
    def __init__(self) -> None:
        super().__init__()


    def init(self):
        raise NotImplementedError()


    def run(self) -> None:
        ''''''
        self.init()
        loop = asyncio.get_event_loop()
        loop.run_forever()