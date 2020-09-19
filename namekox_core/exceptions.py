#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import inspect


reg_exc_map = {}


def gen_exc_dotpath(exc):
    m = inspect.getmodule(exc)
    return '{}.{}'.format(m.__name__, exc.__class__.__name__)


def reg_exc_dotpath(exc):
    p = gen_exc_dotpath(exc)
    reg_exc_map[p] = exc
    return exc


def gen_exc_to_data(exc):
    return {
        'exc_type': exc.__class__.__name__,
        'exc_path': gen_exc_dotpath(exc),
        'exc_args': exc.args,
        'exc_mesg': exc.message
    }


def gen_data_to_exc(data):
    pass


@reg_exc_dotpath
class RemoteError(Exception):
    def __init__(self, exc_type, exc_mesg):
        self.exc_type = exc_type
        self.exc_mesg = exc_mesg
        message = '{} {}'.format(self.exc_type.__name__, self.exc_mesg)
        super(RemoteError, self).__init__(message)
