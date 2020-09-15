#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import six
import sys
import uuid
import inspect
import eventlet


from eventlet import Event
from logging import getLogger
from namekox_core.core.spawning import SpawningProxySet
from namekox_core.core.friendly import ignore_exception
from namekox_core.core.loaders import import_dotpath_class
from namekox_core.constants import SERVICE_CONFIG_KEY, WORKERS_CONFIG_KEY, DEFAULT_WORKERS_NUMBER


from .discovery import is_entrypoint
from .entrypoint import ls_entrypoint_provider
from .dependency import is_dependency, ls_dependency_provider


logger = getLogger(__name__)


class WorkerContext(object):
    _call_id = None
    _call_id_stack = None
    _origin_call_id = None
    _immediate_call_id = None
    _parent_call_id_stack = None

    def __init__(self, service, entrypoint, args=None, kwargs=None, context=None):
        self.args = args or ()
        self.service = service
        self.kwargs = kwargs or {}
        self.entrypoint = entrypoint
        self.context = context or {}

    @property
    def data(self):
        data = self.context.copy()
        data['call_id_stack'] = self.call_id_stack
        return data

    @property
    def call_id(self):
        self._call_id = self._call_id or str(uuid.uuid4())
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
        self._origin_call_id = self._origin_call_id or self.call_id_stack[0]
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
        self._parent_call_id_stack = self._parent_call_id_stack or self.context.pop('call_id_stack', [])
        return self._parent_call_id_stack


class ServiceContainer(object):
    def __init__(self, service_cls, config):
        self.config = config
        self.service_cls = service_cls

        self.started = False
        self.died_event = Event()
        self.being_kill = False
        self.worker_threads = {}
        self.manage_threads = {}
        self.workers = config.get(
            WORKERS_CONFIG_KEY,
            DEFAULT_WORKERS_NUMBER
        )
        self.worker_pool = eventlet.GreenPool(self.workers)

        self.shared_extensions = {}
        self.entrypoints = SpawningProxySet()
        self.dependencies = SpawningProxySet()

        for attr_name, dependency in inspect.getmembers(self.service_cls, is_dependency):
            dependency = dependency.bind(self, attr_name)
            self.dependencies.add(dependency)
            self.dependencies.update(ls_dependency_provider(dependency))
        for method_name, func in inspect.getmembers(self.service_cls, is_entrypoint):
            entrypoints = getattr(func, 'entrypoints', set())
            entrypoints = [entrypoint.bind(self, method_name) for entrypoint in entrypoints]
            [self.entrypoints.add(entrypoint) for entrypoint in entrypoints]
            entrypoints = [ls_entrypoint_provider(entrypoint) for entrypoint in entrypoints]
            [self.entrypoints.update(entrypoint) for entrypoint in entrypoints]

    def start(self):
        self.started = True
        msg = 'starting service {} entrypoints {}'
        logger.debug(msg.format(self.service_cls.name, self.entrypoints))
        self.entrypoints.all.setup()
        self.entrypoints.all.start()
        msg = 'service {} entrypoints {} started'
        logger.debug(msg.format(self.service_cls.name, self.entrypoints))
        
        msg = 'starting service {} dependencies {}'
        logger.debug(msg.format(self.service_cls.name, self.dependencies))
        self.dependencies.all.setup()
        self.dependencies.all.start()
        msg = 'service {} dependencies {} started'
        logger.debug(msg.format(self.service_cls.name, self.dependencies))

    def stop(self):
        if self.died_event.ready():
            msg = 'service {} already stopped'
            logger.debug(msg.format(self.service_cls.name))
            return
        if self.being_kill:
            msg = 'service {} already being kill, wait'
            logger.debug(msg.format(self.service_cls.name))
            ignore_exception(self.died_event.wait)()
            return
        
        msg = 'stopping service {} entrypoints {}'
        logger.debug(msg.format(self.service_cls.name, self.entrypoints))
        self.entrypoints.all.stop()
        msg = 'wait service {} entrypoints {} stop'
        logger.debug(msg.format(self.service_cls.name, self.entrypoints))
        self.worker_pool.waitall()
        msg = 'service {} entrypoints {} stopped'
        logger.debug(msg.format(self.service_cls.name, self.entrypoints))

        msg = 'stopping service {} dependencies {}'
        logger.debug(msg.format(self.service_cls.name, self.dependencies))
        self.dependencies.all.stop()
        msg = 'service {} dependencies {} stopped'
        logger.debug(msg.format(self.service_cls.name, self.dependencies))

        self._kill_manage_threads()

        self.started = False
        self.died_event.ready() or self.died_event.send(None)

    def kill(self):
        if self.died_event.ready():
            msg = 'service {} already stopped'
            logger.debug(msg.format(self.service_cls.name))
            return
        if self.being_kill:
            msg = 'service {} already being kill, wait'
            logger.debug(msg.format(self.service_cls.name))
            ignore_exception(self.died_event.wait)()
            return
        self.being_kill = True

        msg = 'killing service {} entrypoints {}'
        logger.debug(msg.format(self.service_cls.name, self.entrypoints))
        ignore_exception(self.entrypoints.all.kill)()
        ignore_exception(self._kill_worker_threads)()
        msg = 'service {} entrypoints {} killed'
        logger.debug(msg.format(self.service_cls.name, self.entrypoints))

        msg = 'killing service {} dependencies {}'
        logger.debug(msg.format(self.service_cls.name, self.dependencies))
        ignore_exception(self.dependencies.all.kill())
        msg = 'service {} dependencies {} killed'
        logger.debug(msg.format(self.service_cls.name, self.dependencies))

        ignore_exception(self._kill_manage_threads)()

        self.started = False
        self.died_event.ready() or self.died_event.send(None)

    def wait(self):
        return self.died_event.wait()

    def _kill_worker_threads(self):
        if not self.worker_threads:
            return
        for gt, _ in six.iteritems(self.worker_threads):
            gt.kill()

    def _kill_manage_threads(self):
        if not self.manage_threads:
            return
        for gt, _ in six.iteritems(self.manage_threads):
            gt.kill()

    def _link_worker_results(self, gt, ctx):
        self.worker_threads.pop(gt, None)
    
    def _link_manage_results(self, gt, tid):
        self.manage_threads.pop(gt, None)

    def spawn_manage_thread(self, fn, args=None, kwargs=None, tid=None):
        tid, args, kwargs = tid or getattr(fn, '__name__', '<unknown>'), args or (), kwargs or {}
        gt = eventlet.spawn(fn)
        msg = 'spawn manage thread handle {}:{}:{}(args={}, kwargs={}, tid={})'.format(
            self.service_cls.name, fn.__module__, fn.__name__, args, kwargs, tid
        )
        logger.debug(msg)
        self.manage_threads[gt] = tid
        gt.link(self._link_manage_results, tid)
        return gt
    
    def start_worker_thread(self, context, res_handler=None):
        for provider in self.dependencies:
            provider.worker_setup(context)
        result = exc_info = None
        method_name = context.entrypoint.method_name
        method = getattr(context.service, method_name)
        try:
            result = method(*context.args, **context.kwargs)
        except Exception:
            exc_info = sys.exc_info()
        if res_handler is not None:
            result, exc_info = res_handler(result, exc_info)
        for provider in self.dependencies:
            provider.worker_result(context, result, exc_info)
        for provider in self.dependencies:
            provider.worker_teardown(context)
        del exc_info

    def spawn_worker_thread(self, entrypoint, args, kwargs, ctx_data=None, res_handler=None):   
        if self.being_kill:
            return
        service = self.service_cls()
        context = WorkerContext(service, entrypoint, args, kwargs, context=ctx_data)
        msg = 'spawn worker thread handle {}:{}(args={}, kwargs={}, context={})'.format(
            self.service_cls.name, entrypoint.method_name, args, kwargs, ctx_data
        )
        logger.debug(msg)
        gt = self.worker_pool.spawn(self.start_worker_thread, context, res_handler)
        gt.link(self._link_worker_results, context)
        self.worker_threads[gt] = context
        return gt


def get_container_cls(config):
    cls_path = config.get(SERVICE_CONFIG_KEY, {}).get('container_cls', '')
    err, cls = import_dotpath_class(cls_path, ServiceContainer)
    msg = 'load container class from {}:{}'.format(cls.__module__, cls.__name__)
    logger.debug(msg)
    return cls
