#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import inspect


from logging import getLogger
from functools import partial
from types import FunctionType
from eventlet.event import Event


from .extension import Extension


logger = getLogger(__name__)


class Entrypoint(Extension):
    method_name = None

    def __init__(self, *args, **kwargs):
        super(Entrypoint, self).__init__(*args, **kwargs)

    def bind(self, container, name):
        ins = super(Entrypoint, self).bind(container, name)
        ins.method_name = ins.obj_name
        return ins

    def bind_sub_providers(self, obj, container):
        providers = inspect.getmembers(self, is_entrypoint_provider)
        for name, provider in providers:
            setattr(obj, name, provider.bind(container, name))
        return obj

    @classmethod
    def decorator(cls, *args, **kwargs):
        def register_entrypoint(cls_args, cls_kwargs, func):
            entrypoint = cls(*cls_args, **cls_kwargs)
            entrypoints = getattr(func, 'entrypoints', set())
            entrypoints.add(entrypoint)
            setattr(func, 'entrypoints', entrypoints)
            return func
        if len(args) == 1 and isinstance(args[0], FunctionType):
            return register_entrypoint((), {}, args[0])
        return partial(register_entrypoint, args, kwargs)


class EntrypointProvider(Extension):
    def __init__(self, *args, **kwargs):
        super(EntrypointProvider, self).__init__(*args, **kwargs)
        self.entrypoints = set()
        self.entrypoints_reg = False
        self.entrypoints_all_stopped_event = Event()
    
    def register_entrypoint(self, e):
        self.entrypoints.add(e)
        self.entrypoints_reg = True
    
    def wait_entrypoints_stop(self):
        self.entrypoints_reg and self.entrypoints_all_stopped_event.wait()

    def unregister_entrypoint(self, e):
        self.entrypoints.discard(e)
        not self.entrypoints and self.entrypoints_all_stopped_event.send(None)

    def bind_sub_providers(self, obj, container):
        providers = inspect.getmembers(self, is_entrypoint_provider)
        for name, provider in providers:
            setattr(obj, name, provider.bind(container, name))
        return obj


def is_entrypoint(obj):
    return isinstance(obj, Entrypoint)


def is_entrypoint_provider(obj):
    return isinstance(obj, EntrypointProvider)


def ls_entrypoint_provider(obj):
    for name, provider in inspect.getmembers(obj, is_entrypoint_provider):
        for name, sub_provider in ls_entrypoint_provider(provider):
            yield sub_provider.bind(obj.container, name)
        yield provider.bind(obj.container, name)
