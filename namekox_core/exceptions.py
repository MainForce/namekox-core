#! -*- coding: utf-8 -*-

# author: forcemain@163.com


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
    exc_mesg = data['exc_mesg']
    return RemoteError(exc_type, exc_mesg)


class RemoteError(Exception):
    def __init__(self, exc_type, exc_mesg):
        exc_mesg = exc_mesg.replace(self.__class__.__name__, '')
        exc_mesg = exc_mesg.strip()
        self.exc_type = exc_type
        self.exc_mesg = exc_mesg
        message = '{} {}'.format(self.exc_type, self.exc_mesg)
        super(RemoteError, self).__init__(message)
