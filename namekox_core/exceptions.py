#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import six
import inspect


def gen_exc_dotpath(exc):
    m = inspect.getmodule(exc)
    if m is None:
        dotpath = exc.__class__.__name__
    else:
        dotpath = '{}.{}'.format(
            m.__name__,
            exc.__class__.__name__
        )
    return dotpath


def set_exc_to_repr(arg):
    return arg if isinstance(arg, six.string_types) else repr(arg)


def gen_exc_to_data(exc):
    return {
        'exc_type': exc.__class__.__name__,
        'exc_path': gen_exc_dotpath(exc),
        'exc_args': [set_exc_to_repr(arg) for arg in exc.args],
        'exc_mesg': set_exc_to_repr(exc.message)
    }


def gen_data_to_exc(data):
    exc_type = data['exc_type']
    # fix type() argument 1 must be string, not unicode
    exc_type = str(exc_type)
    exc_klss = type(exc_type, (Exception,), {})
    exc_mesg = data['exc_mesg']
    return exc_klss(exc_mesg)
