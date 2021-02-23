#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import inspect


from logging import getLogger
from functools import partial
from types import FunctionType


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
        provider_obj = provider.bind(obj.container, name)
        setattr(obj, name, provider_obj)
        yield provider_obj
        for sub_provider in ls_entrypoint_provider(provider_obj): yield sub_provider

