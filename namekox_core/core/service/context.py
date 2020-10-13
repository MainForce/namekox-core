#! -*- coding: utf-8 -*-

# author: forcemain@163.com


from namekox_core.core.generator import generator_uuid


class BaseContext(object):
    _call_id = None
    _call_id_stack = None
    _origin_call_id = None
    _immediate_call_id = None
    _parent_call_id_stack = None

    def __init__(self, context=None):
        self.context = context or {}

    @property
    def data(self):
        data = self.context.copy()
        data['call_id_stack'] = self.call_id_stack
        return data

    @property
    def call_id(self):
        if self._call_id is None:
            self._call_id = generator_uuid()
        return self._call_id

    @property
    def call_id_stack(self):
        if self._call_id_stack is None:
            self._call_id_stack = []
            self._call_id_stack.extend(self.parent_call_id_stack)
            self._call_id_stack.append(self.call_id)
        return self._call_id_stack

    @property
    def origin_call_id(self):
        if self._origin_call_id is None:
            self._origin_call_id = self.call_id_stack[0]
        return self._origin_call_id

    @property
    def immediate_call_id(self):
        if self._immediate_call_id is None:
            stack = self.call_id_stack
            stack_length = len(stack)
            self._immediate_call_id = stack[0] if stack_length > 1 else None
        return self._immediate_call_id

    @property
    def parent_call_id_stack(self):
        if self._parent_call_id_stack is None:
            self._parent_call_id_stack = self.context.pop('call_id_stack', [])
        return self._parent_call_id_stack


class WorkerContext(BaseContext):
    def __init__(self, service, entrypoint, args=None, kwargs=None, context=None):
        self.args = args or ()
        self.service = service
        self.kwargs = kwargs or {}
        self.entrypoint = entrypoint
        super(WorkerContext, self).__init__(context)
