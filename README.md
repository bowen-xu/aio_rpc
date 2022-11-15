# aio_rpc

Remote Procedure Caller based-on Asynchronous IO and Socket

## Quick Start



## APIs

#### `AioRpcNode`

This is an abstract class, which should not be instantiated directly. This class is succeeded by `AioRpcServer` and `AioRpcClient`, which are classes for server and client correspondingly.

##### `run`

Once you instantiate an `AioRpcServer` or an `AioRpcClient`, you can call the method `run` to start the server or the client. This method starts an `event_loop` of `asyncio`, so the program would be blocked after starting. If you wish to start the loop later at another place, you should call the method `init` to initialize the server/client.

#### `AioRpcServer(AioRpcNode)`

##### `__init__`

##### `add`

##### `remove`

##### `register`

##### `init`

To initialize the server, this method create an (asynchronous) socket through `aiosock`, and cache the IP and port into a file, so that clients can reach the file and then connect to the server socket.


#### `AioRpcClient(AioRpcNode)`

##### `__init__`

##### `init`

##### `call`


