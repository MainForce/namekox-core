#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import eventlet


class SpawningProxySet(set):
    @property
    def all(self):
        return SpawningProxy(self)
    
    def __str__(self):
        return '{}'.format(list(self))
    
    def __repr__(self):
        return '{}'.format(list(self))


class SpawningProxy(object):
    def __init__(self, items=None):
        self.items = items

    def __str__(self):
        return '{}'.format(list(self.items))
    
    def __repr__(self):
        return '{}'.format(list(self.items))

    def __getattr__(self, name):
        def spawning_method(*args, **kwargs):
            if not self.items:
                return
            pool = eventlet.GreenPool(len(self.items))

            def call(item):
                return getattr(item, name)(*args, **kwargs)

            return list(pool.imap(call, self.items))
        return spawning_method
