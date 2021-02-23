#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import six
import inspect


from importlib import import_module
from namekox_core.core.loaders import import_dotpath_class


if six.PY2:
    is_method = inspect.ismethod
else:
    is_method = inspect.isfunction


def is_entrypoint(obj):
    return is_method(obj) and hasattr(obj, 'entrypoints')


def is_service(obj):
    is_class = isinstance(obj, six.class_types)
    has_name = hasattr(obj, 'name')
    has_work = inspect.getmembers(obj, is_entrypoint)
    return is_class and has_name and has_work


def find_services(module_name):
    services = []
    parts = module_name.rsplit(':', 1)
    if len(parts) == 1:
        m_path, c_name = module_name, None
    else:
        m_path, c_name = parts[0], parts[1]
    if c_name is not None:
        err, obj = import_dotpath_class(module_name)
        return err, [obj] if is_service(obj) else []
    try:
        obj = import_module(module_name)
    except ImportError as e:
        err = e.message
        return err, services
    err = None
    return err, [srv for _, srv in inspect.getmembers(obj, is_service)]
