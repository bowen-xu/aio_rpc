import inspect
from aio_rpc import AioRpcServer, rpc

server = AioRpcServer()

@rpc(server, "test")
def print_test(content):
    print("hello world!", content)
    return str(content)


@rpc(server, 0)
def test0():
    pass

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


server.run()
