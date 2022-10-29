
from pydoc import cli
from aiosock import asyncio
from aio_rpc import AioRpcClient, RpcServerObject
from time import time
import aiosock

def callback(data):
    print(data)

client = AioRpcClient()

client.init()


def main():
    client.call_func(1, callback)
    client.call_func("test", callback, RpcServerObject(client.id))

async def main2():
    s = await client.async_call_func(1)
    print('async', s)

loop = asyncio.get_event_loop()
loop.call_soon(main)
loop.create_task(main2())
loop.run_forever()
# n = 100000
# t1 = time()
# for _ in range(n):
#     client.call(0)
# t2 = time()
# print((t2-t1)/n, n/(t2-t1))