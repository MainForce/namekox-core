#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


from importlib import import_module


def import_dotpath_class(path, default=None):
    parts = path.rsplit(':', 1)
    if len(parts) == 1:
        m_path, c_name = path, None
    else:
        m_path, c_name = parts[0], parts[1]
    if c_name is None:
        error = '{} ≠ <module>:<service class>'.format(path)
        return error, default
    try:
        module = import_module(m_path)
    except ImportError as e:
        error = e.message
        return error, default
    if not hasattr(module, c_name):
        error = '{} has no attribute {}'.format(m_path, c_name)
        return error, default
    error = None
    return error, getattr(module, c_name) or default
