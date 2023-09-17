import asyncio
from aio_rpc import AioRpcClient, RpcServerObject, rpc
from time import time

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

async def main3():
    foo = await client.async_instantiate('Foo')
    print(foo)
    print(await client.async_call_async_method(foo, 3))
    print(await client.async_call_method(foo, 4))

@rpc(client, "test")
def test(msg):
    print(msg)
    return "return from client"

loop = asyncio.get_event_loop()
loop.call_soon(main)
loop.run_until_complete(main2())
loop.run_until_complete(main3())
loop.run_until_complete(client.async_call_async_func("call_client", client.id))