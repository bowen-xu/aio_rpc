
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
    print('main')
    client.call_func(1, callback)
    client.call_func("test", callback, RpcServerObject(client.id))

async def main2():
    s = await client.async_call_func(1)
    print('async', s)

async def test_benchmark():
    n = 10000
    t1 = time()
    for _ in range(n):
        await client.async_call_func(0, None, 1, 2)
    t2 = time()
    print(f"{(t2-t1)/n} s/seq, {n/(t2-t1)} seq/s")

loop = asyncio.get_event_loop()
loop.call_soon(main)
loop.run_until_complete(main2())
loop.run_until_complete(test_benchmark())