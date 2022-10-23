
from multiprocessing import Process
import asyncio

class AioRpcNode(Process):
    def __init__(self) -> None:
        super().__init__()

    
    def run(self) -> None:
        ''''''
        self.init()
        loop = asyncio.get_event_loop()
        loop.run_forever()