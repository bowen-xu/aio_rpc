# as_rpc

`as_rpc` is a python package for Remote Procedure Call (RPC) based-on *Asynchronous IO* and *Socket*.

It supports bidirectional calls, and it has very high efficiency.

## Quick Start

To install `as-rpc`, run the command

```
pip install as-rpc
```

Let's run the program first, and then some more details on how to use `as-rpc` will be given.

Suppose we have two files, one for server and the other for client.

Server Example (see also `test_server.py`)
```Python
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
```

Client Example (see also `test_client.py`)
```Python
import asyncio
from as_rpc import AioRpcClient, RpcServerObject, rpc
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
```

In one terminal, run the command
```
python test_server.py
```

In another terminal, run the command
```
python test_client.py
```

You will see the outputs from the server

```
this is test1.
hello world! None
this is test1.
this is test3.
this is test4.
call client
return from client
```
and the outputs from the client
```
main
('this is test1.', None)
('None', None)
async this is test1.
-8991251603859186137
this is test3.
this is test4.
msg from server
```

In the client, the program calls some functions in the server, gets the return values, and prints them.

### Create and Run a Server/Client

To create a server, first import related objects
```Python
from as_rpc import AioRpcServer, rpc
```
and then instantiate a server by
```Python
server = AioRpcServer()
```

To run the server, you can either call `server.init()` and then start the event-loop of `asyncio`
```Python
server.init()
loop = asyncio.get_event_loop()
loop.run_forever()
```
or just call `server.run()` which packs the code above
```Python
server.run()
```

To create a client, first import related objects
```Python
from as_rpc import AioRpcClient, rpc
```
and then instantiate a client by
```Python
client = AioRpcClient()
```

To run the client, call `client.init()` and then start the event-loop of `asyncio`
```Python
client.init()
loop = asyncio.get_event_loop()
loop.run_forever()
```

### Register Functions

You can register a function or async function by adding a *decorator* on a function, for example
```Python
@rpc(server, 0)
def test0(*args):
    return 0

@rpc(server, "test1")
async def test1(*args):
    return 1
```
In `@rpc(server, name)`, the first parameter is the server instance, while the second parameter is the name denoting the corresponding function. Client can call this function by the name defined here. For example, in client
```Python
s = await client.async_call_async_func("test1")
```
There are four types of calling a function: `call_func()`, `async_call_func()`, `call_async_func()`, and `async_call_async_func()`. The meaning of them will be illustrated later (see the section "**Call Functions**").

In client programe, functions can also be registered in the same way.
```Python
@rpc(client, "test")
def test(msg):
    print(msg)
    return "return from client"
```

### Call Functions

For a client, there are four types of calling a function:
- `call_func(name_func, callback, *args)`: call a normal function directly in the remote. The first parameter is the function name in the remote (server or client); the second parameter `callback` is a function which would be called after the result from the remote is returned. It could be `None` if the returned value is not concerned. The subsequent `args` is a list of arguments passed to the remote.
- `async_call_func(name_func, *args)`: call a normal function asynchronously in the remote. You can use `await async_call_func(...)` to get the returned value, so there is no need to claim the callback function.
- `call_async_func(name_func, callback, *args)`: call an async function directly in the remote. The function in the remote is asynchronous, defined with keyword `async`. The parameters are the same as `call_func()`.
- `async_call_async_func(name_func, *args)`: call an async function asynchronously in the remote. The parameters are the same as `call_async_func()`.

For a server, there are also four types of calling a function, with the same names as the above. The difference is that there is an additional parameter in the first postion of each of the four, i.e., `client_id`. 
- `call_func(client_id, name_func, callback, *args)`,
- `async_call_func(client_id, name_func, *args)`,
- `call_async_func(client_id, name_func, callback, *args)`,
- `async_call_async_func(client_id, name_func, *args)`.

The parameter `client_id` determines which client to call.

An example of calling a function by server is
```Python
@rpc(server, "call_client")
async def call_client(client_id):
    print("call client")
    msg = await server.async_call_func(client_id, "test", "msg from server")
    print(msg)
```

All the clients' ids are avaible through `server.clients.keys()`.

### Instantiate Classes and Call Methods

For a client, you can create an instance of class in the remote by `instantiate(<Remote-Class-Marker>)` or `async_instantiate(<Remote-Class-Marker>)`. The returned value is the handler of the remote instance.

To call a method of it, you can use the four
- `call_method(self, name_self, name_method, callback, *args)`,
- `async_call_method(self, name_self, name_method, *args)`,
- `call_async_method(self, name_self, name_method, callback, *args)`,
- `async_call_async_method(self, name_self, name_method, *args)`.

The difference among the four types is similar to the previous.

An example to instantiate a class and to call methods is
```Python
foo = await client.async_instantiate('Foo')
print(foo)
print(await client.async_call_async_method(foo, 3))
print(await client.async_call_method(foo, 4))
```

For a server, you can do similar things, except that you need to pass a parameter `client_id` for each calling.

That's all about the usage of as-rpc. You can raise issues in the github repo if you have questions, want to report bugs, or need more features.

## Benchmark

| Framework | Speed (req/s) |
| ---- | ----- |
| [zero (v0.4.1)](https://github.com/Ananto30/zero) | 2173 |
| as-rpc (this repo) | *10244* |