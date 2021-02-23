#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import inspect


from .extension import Extension


class Dependency(Extension):
    attr_name = None

    def __init__(self, *args, **kwargs):
        super(Dependency, self).__init__(*args, **kwargs)

    def bind(self, container, name):
        ins = super(Dependency, self).bind(container, name)
        ins.attr_name = ins.obj_name
        return ins

    def bind_sub_providers(self, obj, container):
        providers = inspect.getmembers(self, is_dependency_provider)
        for name, provider in providers:
            setattr(obj, name, provider.bind(container, name))
        return obj

    def get_instance(self, context):
        return self

    def worker_setup(self, context):
        pass

    def worker_teardown(self, context):
        pass

    def worker_result(self, context, result=None, exc_info=None):
        pass


class DependencyProvider(Dependency):
    pass


def is_dependency(obj):
    return isinstance(obj, Dependency)


def is_dependency_provider(obj):
    return isinstance(obj, DependencyProvider)


def ls_dependency_provider(obj):
    for name, provider in inspect.getmembers(obj, is_dependency_provider):
        provider_obj = provider.bind(obj.container, name)
        setattr(obj, name, provider_obj)
        yield provider_obj
        for sub_provider in ls_dependency_provider(provider_obj): yield sub_provider
