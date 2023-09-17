from as_rpc import AioRpcServer, rpc
import asyncio

server = AioRpcServer()

@rpc(server, "test")
def print_test(content):
    print("hello world!", content)
    return str(content)


@rpc(server, 0)
def test0(*args):
    return 1

@rpc(server, 1)
def test1():
    s = "this is test1."
    print(s)
    return s

@rpc(server, 2)
async def test2():
    s = "this is test2."
    print(s)
    return s

@rpc(server, 'Foo')
class Foo:
    @rpc(server, 3)
    async def test3(self):
        s = "this is test3."
        print(s)
        return s
    
    @rpc(server, 4)
    def test4(self):
        s = "this is test4."
        print(s)
        return s

@rpc(server, "call_client")
async def call_client(client_id):
    print("call client")
    msg = await server.async_call_func(client_id, "test", "msg from server")
    print(msg)

server.run()
