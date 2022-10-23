
from aiosock import asyncio
from aio_rpc import AioRpcClient
from time import time
import aiosock

def callback(data):
    print(data)

client = AioRpcClient()

client.init()

def main():
    client.call(1, callback)

loop = asyncio.get_event_loop()
loop.call_soon(main)
loop.run_forever()
# n = 100000
# t1 = time()
# for _ in range(n):
#     client.call(0)
# t2 = time()
# print((t2-t1)/n, n/(t2-t1))