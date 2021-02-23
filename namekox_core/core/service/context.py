#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


from namekox_core.core.generator import generator_uuid


class BaseContext(object):
    _call_id = None
    _parent_call_id = None

    def __init__(self, context=None):
        self.context = context or {}

    @property
    def call_id(self):
        self._call_id = self._call_id or generator_uuid()
        return self._call_id

    @property
    def parent_call_id(self):
        self._parent_call_id = self._parent_call_id or self.context.get('call_id', None)
        return self._parent_call_id

    @property
    def data(self):
        data = self.context.copy()
        data.update({'call_id': self.call_id, 'parent_call_id': self.parent_call_id})
        return data


class WorkerContext(BaseContext):
    def __init__(self, service, entrypoint, args=None, kwargs=None, context=None):
        self.args = args or ()
        self.service = service
        self.kwargs = kwargs or {}
        self.entrypoint = entrypoint
        super(WorkerContext, self).__init__(context)
