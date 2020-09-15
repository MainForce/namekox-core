#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import weakref


class Extension(object):
    _params = None
    obj_name = None
    container = None

    def __new__(cls, *args, **kwargs):
        instance = super(Extension, cls).__new__(cls, *args, **kwargs)
        instance._params = (args, kwargs)
        return instance

    def setup(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def kill(self):
        pass

    def bind(self, container, name):
        def clone(obj):
            if obj.container is not None:
                return obj
            cls = type(obj)
            cls_args, cls_kwargs = self._params
            ext = cls(*cls_args, **cls_kwargs)
            ext.container = weakref.proxy(container)
            return ext
        ins = clone(self)
        ins.obj_name = name
        ins = self.bind_sub_providers(ins, container)
        return ins

    def bind_sub_providers(self, obj, container):
        return obj

    def __str__(self):
        name = '{}.{}'.format(self.__module__, self.__class__.__name__)
        return '{}:{}:{}'.format(self.container.service_cls.name, name, self.obj_name)

    def __repr__(self):
        name = '{}.{}'.format(self.__module__, self.__class__.__name__)
        return '{}:{}:{}'.format(self.container.service_cls.name, name, self.obj_name)
