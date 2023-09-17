'''
Handler
In multi-process communication, a process calls a function of another process and needs to pass function information through a handler
'''

import hashlib
from typing import Callable, Dict
from bidict import bidict
import inspect
import pickle

def _hash(obj):
    return int(hashlib.sha1(pickle.dumps(obj)).hexdigest(), 16)

handlers: bidict[int, Callable] = bidict()

def register(function: Callable):
    handler, func = _hash_function(function)
    # if handler in handlers:
    #     return handler, handlers[handler]
    # elif func in handlers.inv:
    #     return handlers.inv[func], func
    # else:
    handlers[handler] = func
    return handler, func


def get_handler(function: Callable):
    if inspect.ismethod(function):
        function = function.__func__
    return handlers.inverse.get(function, None)

def get_function(handler: int):
    return handlers.get(handler, None)


def unregister(function: Callable):
    return handlers.pop(_hash_function(function), None)


def _hash_function(function: Callable):
    ''''''
    name_cls=None
    if inspect.ismethod(function):
        func = function.__func__
        # name_cls = function.__self__.__class__.__name__
        # name_cls = function.__qualname__.split('.')[-2] # function.__self__.__class__.__name__
    else:
        func = function
    name_module = func.__module__
    name_func = func.__qualname__
    if name_module == '__main__': 
        name_module = name_func.split('.')[0]
    # name_func = func.__name__
    return _hash((name_module, name_cls, name_func)), func
