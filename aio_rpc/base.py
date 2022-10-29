
from multiprocessing import Process
from asyncio import Event
import asyncio
from pathlib import Path
from typing import Any, Callable, Dict, Tuple
from uuid import uuid1, uuid4
from aiosock import AioSock
from .utils import MsgType  

def _asynchronify(_call, pos_callback):
    ''''''
    def wrapper(_func):
        ''''''
        async def async_call(self, *args):
            event = Event()
            event.clear()
            obj_id = None
            def callback(_obj_id):
                ''''''
                nonlocal obj_id
                obj_id = _obj_id
                event.set()
            _call(self, *args[:pos_callback], callback, *args[pos_callback:])
            await event.wait()
            return obj_id
        return async_call
    return wrapper
    
class AioRpcBase(Process):
    def __init__(self) -> None:
        super().__init__()
        
        self.funcs = {}
        self.func_async = {}

        self.classes = {}
        self.objs = {}

        self.loop: asyncio.BaseEventLoop = None

        self.callbacks: Dict[int, Callable] = {}

        self.msg_handlers = {
            MsgType.Func: self._handle_msg__Func,
            MsgType.AsyncFunc: self._handle_msg__AsyncFunc,
            MsgType.Method: self._handle_msg__Method,
            MsgType.AsyncMethod: self._handle_msg__AsyncMethod,
            MsgType.Class: self._handle_msg__Class,
            MsgType.Return: self._handle_msg__Return
        }
        self.id = hash((uuid1(), uuid4()))
        self.objs[self.id] = self

    def init(self):
        raise NotImplementedError()


    def _on_sock_recv(self, data: Tuple[MsgType, int, Any, Tuple], ssock: AioSock):
        ''''''
        msg_type = data[0]
        msg_handler = self.msg_handlers.get(msg_type, None)
        if msg_handler is not None:
            msg_handler(data, ssock)


    def _handle_msg__Func(self, data, ssock: AioSock):
        _, pack_id, name, args = data
        func = self.funcs.get(name, None)
        ret = func(*args)
        if pack_id is not None:
            ssock.write((MsgType.Return, pack_id, ret))


    def _handle_msg__AsyncFunc(self, data, ssock: AioSock):
        _, pack_id, name, args = data
        func_async = self.func_async.get(name, None)
        async def wrapper(func, args):
            ret = await func(*args)
            if pack_id is not None:
                ssock.write((MsgType.Return, pack_id, ret))
        self.loop.create_task(wrapper(func_async, args))


    def _handle_msg__Method(self, data, ssock: AioSock):
        _, pack_id, name_obj, name_method, args = data
        method = self.funcs.get(name_method, None)
        obj = self.objs.get(name_obj, None)
        ret = method(obj, *args)
        if pack_id is not None:
            ssock.write((MsgType.Return, pack_id, ret))


    def _handle_msg__AsyncMethod(self, data, ssock: AioSock):
        _, pack_id, name_obj, name_method, args = data
        method_async = self.func_async.get(name_method, None)
        obj = self.objs.get(name_obj, None)
        async def wrapper(obj, func, args):
            ret = await func(obj, *args)
            if pack_id is not None:
                ssock.write((MsgType.Return, pack_id, ret))
        self.loop.create_task(wrapper(obj, method_async, args))


    def _handle_msg__Class(self, data, ssock: AioSock):
        _, pack_id, name_class, args = data
        cls = self.classes.get(name_class, None)
        obj = cls(*args)
        obj_id = hash((uuid1(), uuid4()))
        self.objs[obj_id] = obj

        if pack_id is not None:
            ssock.write((MsgType.Return, pack_id, obj_id))


    def _handle_msg__Return(self, data, ssock: AioSock):
        _, pack_id, ret = data
        if pack_id is None: return
        callback = self.callbacks.pop(pack_id, None)
        if callback is not None:
            callback(ret)


    def run(self) -> None:
        ''''''
        self.init()
        loop = asyncio.get_event_loop()
        loop.run_forever()


    def _new_pack_id(self, callback):
        if callback is not None:
            pack_id = hash((uuid1(), uuid4()))
            self.callbacks[pack_id] = callback
        else: 
            pack_id = None
        return pack_id


    def reset(self, root='cache/io_process/', name='IOP0'):
        ''''''
        self.root = Path(root)
        self.name = name
        self.root.mkdir(parents=True, exist_ok=True)

    def add(self, func, name):
        ''''''
        self.funcs[name] = func
    

    def add_async(self, func_coro, name):
        ''''''
        self.func_async[name] = func_coro


    def add_class(self, cls, name):
        ''''''
        self.classes[name] = cls
    
    def add_obj(self, obj, name):
        self.objs[name] = obj