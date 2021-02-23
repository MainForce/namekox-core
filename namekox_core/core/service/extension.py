#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import weakref


from eventlet.event import Event


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
        name = '{}.{}'.format(self.__class__.__module__, self.__class__.__name__)
        return '{}:{}:{}'.format(self.container.service_cls.name, name, self.obj_name)

    def __repr__(self):
        name = '{}.{}'.format(self.__class__.__module__, self.__class__.__name__)
        return '{}:{}:{}'.format(self.container.service_cls.name, name, self.obj_name)


class SharedExtension(object):
    @property
    def _key(self):
        return self.__class__.__name__

    def bind(self, container, name):
        ins = container.shared_providers.get(self._key, None)
        if ins is None:
            ins = super(SharedExtension, self).bind(container, name)
            container.shared_providers[self._key] = ins
        return ins


class ControlExtension(object):
    def __init__(self, *args, **kwargs):
        super(ControlExtension, self).__init__(*args, **kwargs)
        self.extensions = set()
        self.extensions_reg = False
        self.extensions_all_stopped_event = Event()

    def register_extension(self, e):
        self.extensions.add(e)
        self.extensions_reg = True

    def wait_extension_stop(self):
        self.extensions_reg and self.extensions_all_stopped_event.wait()

    def unregister_extension(self, e):
        self.extensions.discard(e)
        not self.extensions and self.extensions_all_stopped_event.send(None)
