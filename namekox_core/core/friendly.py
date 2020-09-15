#! -*- coding: utf-8 -*-

# author: forcemain@163.com


def ignore_exception(func):
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
        except:
            pass
        return result
    return wrapper
