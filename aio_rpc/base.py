
from multiprocessing import Process
from asyncio import Event
import asyncio
from pathlib import Path
from typing import Any, Callable, Dict, Tuple
from uuid import uuid1, uuid4
from aiosock import AioSock
from .utils import MsgType  
import traceback
from .progress import Progress
from collections import defaultdict
from . import handler

def _asynchronify(_call, pos_callback):
    ''''''
    def wrapper(_func):
        ''''''
        async def async_call(self, *args):
            event = Event()
            event.clear()
            obj_id = None
            err = None
            def callback(data):
                ''''''
                nonlocal obj_id
                nonlocal err
                nonlocal event
                # obj_id, err = data
                _obj_id, err = data
                # if err: 
                #     raise err
                event.set()
                obj_id = _obj_id
            _call(self, *args[:pos_callback], callback, *args[pos_callback:])
            await event.wait()
            if err:
                raise err
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

        self.progresses = defaultdict(Progress)
        h, f = handler.register(self._get_local_progress)
        self.add(f, h)
        h, f = handler.register(self._add_local_progress)
        self.add(f, h)

        self.init_ok = Event()
        self.init_ok.clear()


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
        try:
            ret = func(*args)
        except Exception as e:
            e.args = tuple((*e.args, ('traceback', traceback.format_exc())))
            if pack_id is not None:
                ssock.write((MsgType.Return, pack_id, (None, e)))
            return
        if pack_id is not None:
            ssock.write((MsgType.Return, pack_id, (ret, None)))


    def _handle_msg__AsyncFunc(self, data, ssock: AioSock):
        _, pack_id, name, args = data
        func_async = self.func_async.get(name, None)
        async def wrapper(func, args):
            try:
                ret = await func(*args)
            except Exception as e:
                e.args = tuple((*e.args, ('traceback', traceback.format_exc())))
                if pack_id is not None:
                    ssock.write((MsgType.Return, pack_id, (None, e)))
                return
            if pack_id is not None:
                ssock.write((MsgType.Return, pack_id, (ret, None)))
        self.loop.create_task(wrapper(func_async, args))


    def _handle_msg__Method(self, data, ssock: AioSock):
        _, pack_id, name_obj, name_method, args = data
        method = self.funcs.get(name_method, None)
        if method is None:
            ssock.write((MsgType.Return, pack_id, (None, Exception("RPC call methoed error: method unfound. Please ensure that the server/clinet has been fully initialized and the method is registered."))))
            return
        obj = self.objs.get(name_obj, None)
        if obj is None:
            ssock.write((MsgType.Return, pack_id, (None, Exception("RPC call methoed error: object unfound. Please ensure that the server/clinet has been fully initialized and the method is registered."))))
            return

        try:
            ret = method(obj, *args)
        except Exception as e:
            e.args = tuple((*e.args, ('traceback', traceback.format_exc())))
            if pack_id is not None:
                ssock.write((MsgType.Return, pack_id, (None, e)))
            else:
                print(e)
            return
        if pack_id is not None:
            ssock.write((MsgType.Return, pack_id, (ret, None)))


    def _handle_msg__AsyncMethod(self, data, ssock: AioSock):
        _, pack_id, name_obj, name_method, args = data
        method_async = self.func_async.get(name_method, None)
        if method_async is None:
            ssock.write((MsgType.Return, pack_id, (None, Exception("RPC call aync methoed error: method unfound. Please ensure that the server/clinet has been fully initialized and the method is registered."))))
            return
        obj = self.objs.get(name_obj, None)
        if obj is None:
            ssock.write((MsgType.Return, pack_id, (None, Exception("RPC call aync methoed error: object unfound. Please ensure that the server/clinet has been fully initialized and the method is registered."))))
            return

        async def wrapper(obj, func, args):
            try:
                ret = await func(obj, *args)
            except Exception as e:
                e.args = tuple((*e.args, ('traceback', traceback.format_exc())))
                if pack_id is not None:
                    ssock.write((MsgType.Return, pack_id, (None, e)))
                return
            if pack_id is not None:
                ssock.write((MsgType.Return, pack_id, (ret, None)))
        self.loop.create_task(wrapper(obj, method_async, args))


    def _handle_msg__Class(self, data, ssock: AioSock):
        _, pack_id, name_class, args = data
        try:
            cls = self.classes.get(name_class, None)
            obj = cls(*args)
            obj_id = hash((uuid1(), uuid4()))
            self.objs[obj_id] = obj
        except Exception as e:
            e.args = tuple((*e.args, ('traceback', traceback.format_exc())))
            if pack_id is not None:
                ssock.write((MsgType.Return, pack_id, (None, e)))
            return
        if pack_id is not None:
            ssock.write((MsgType.Return, pack_id, (obj_id, None)))


    def _handle_msg__Return(self, data, ssock: AioSock):
        _, pack_id, (ret, err) = data
        if pack_id is None: return
        callback = self.callbacks.pop(pack_id, None)
        # if err is not None and callback_err is not None:
        #     callback_err(err)
        if callback is not None:
            callback((ret, err))


    def run(self) -> None:
        ''''''
        self.init()
        loop = asyncio.get_event_loop()
        loop.run_forever()


    def _new_pack_id(self, callback, callback_err=None):
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

    def set_progress(self, name, value=0, done=False):
        '''
        set local progress
        '''
        if not done:
            progress = self.progresses[name]
            progress.set(value)
        else:
            self.progresses.pop(name, None)

    def _get_local_progress(self, name):
        ''''''
        if name in self.progresses:
            return self.progresses[name].value
        else:
            return None
        
    def _add_local_progress(self, name):
        ''''''
        if name not in self.progresses:
            self.progresses[name] = Progress()

    def get_progress(self, name):
        '''
        get remote progress
        '''
        raise NotImplementedError("Virtual Method")
    
    def add_progress(self, name):
        '''
        add remote progress
        '''
        raise NotImplementedError("Virtual Method")
