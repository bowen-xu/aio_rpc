import inspect
from aio_rpc import AioRpcServer, rpc

server = AioRpcServer()


@rpc(server, 0)
def test0():
    pass


server.run()
