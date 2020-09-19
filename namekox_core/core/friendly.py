#! -*- coding: utf-8 -*-

# author: forcemain@163.com


from functools import wraps


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


def ignore_exception(func):
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
        except:
            pass
        return result
    return wrapper
