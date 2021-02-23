#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import sys
import time


from functools import wraps


def ignore_exception(func, exc_func=None, expected_exceptions=(Exception,)):
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
        except expected_exceptions:
            exc_func = wrapper.exc_func
            if callable(exc_func):
                exc_info = sys.exc_info()
                ignore_exception(exc_func)(exc_info)
        return result
    wrapper.exc_func = exc_func
    return wrapper


def as_singleton_cls(cls):
    @wraps(cls)
    def wrapper(*args, **kwargs):
        if not hasattr(cls, '_instance'):
            instance = cls(*args, **kwargs)
            setattr(cls, '_instance', instance)
        else:
            instance = cls._instance
        return instance
    return wrapper


class AsLazyProperty(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        data = self.func(instance)
        setattr(instance, self.func.__name__, data)
        return data


def as_wraps_partial(func, *init_args, **init_kwargs):
    @wraps(func)
    def wrapper(*part_args, **part_kwargs):
        args, kwargs = [], {}
        args.extend(init_args)
        args.extend(part_args)
        kwargs.update(init_kwargs)
        kwargs.update(part_kwargs)
        return func(*args, **kwargs)
    return wrapper


def auto_sleep_retry(func, exc_func=None, expected_exceptions=(Exception,), max_retries=sys.maxsize, time_sleep=None):
    count = 0
    while True:
        if count >= max_retries:
            break
        try:
            func()
            break
        except expected_exceptions:
            if callable(exc_func):
                exc_info = sys.exc_info()
                ignore_exception(exc_func)(exc_info)
        sleep = time_sleep or pow(2, count)
        time.sleep(sleep)
        count += 1
