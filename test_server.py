from aio_rpc import AioRpcServer, rpc

server = AioRpcServer()

@rpc(server, "test")
def print_test(content):
    print("hello world!", content)


@rpc(server, 0)
def test0():
    pass

@rpc(server, 1)
def test1():
    s = "this is test1."
    print(s)
    return s

server.start()