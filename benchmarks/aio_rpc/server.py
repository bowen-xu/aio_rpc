import sys
sys.path.append("../..")
from aio_rpc import AioRpcServer, rpc

server = AioRpcServer()


@rpc(server, 0)
def test0(*args):
    return 1


server.run()
