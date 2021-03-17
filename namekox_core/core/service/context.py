#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


from logging import getLogger
from namekox_core.constants import SERVICE_CONFIG_KEY
from namekox_core.core.generator import generator_uuid
from namekox_core.core.loaders import import_dotpath_class


logger = getLogger(__name__)


class WorkerContext(object):
    _call_id = None
    _origin_id = None
    _parent_call_id = None

    def __init__(self, service, entrypoint, args=None, kwargs=None, context=None):
        self.args = args or ()
        self.service = service
        self.context = context
        self.entrypoint = entrypoint
        self.kwargs = kwargs or {}
        self.gen_callid = get_trace_id_func(entrypoint.container.config)

    @property
    def call_id(self):
        self._call_id = self._call_id or self.gen_callid()
        return self._call_id

    @property
    def origin_id(self):
        self._origin_id = self.context.get('origin_id', None) or self.call_id
        return self._origin_id

    @property
    def parent_call_id(self):
        self._parent_call_id = self._parent_call_id or self.context.get('call_id', None)
        return self._parent_call_id

    @property
    def data(self):
        data = self.context.copy()
        data.update({'origin_id': self.origin_id,
                     'call_id': self.call_id,
                     'parent_call_id': self.parent_call_id
                     })
        return data


def get_trace_id_func(config):
    fun_path = config.get(SERVICE_CONFIG_KEY, {}).get('trace_id_func', '')
    err, fun = import_dotpath_class(fun_path, generator_uuid)
    msg = 'load trace id func from {} failed, {}'.format(fun_path, err)
    err and logger.warning(msg)
    return fun
