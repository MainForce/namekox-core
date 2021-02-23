#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import print_function
from __future__ import unicode_literals


import signal
import eventlet
import eventlet.debug


from logging import getLogger
from namekox_core.core.friendly import as_wraps_partial
from namekox_core.core.service.runner import ServiceRunner
from namekox_core.core.service.discovery import find_services
from namekox_core.constants import HUB_ERR_CONFIG_KEY, DEFAULT_HUB_ERR_PRINT


from .base import BaseCommand


logger = getLogger(__name__)


def stop(runner, signum, frame):
    eventlet.spawn_n(runner.stop)


def start(services, config):
    runner = ServiceRunner(config)
    for service in services:
        runner.add_service(service)
    signal.signal(signal.SIGTERM, as_wraps_partial(stop, runner))
    runner.start()
    try:
        runner.wait()
    except KeyboardInterrupt:
        print('\r', end='')
        runner.stop()
    except Exception:
        runner.stop()
    finally:
        runner.kill()


class Run(BaseCommand):
    """ run one or more services """
    @classmethod
    def name(cls):
        return 'run'

    @classmethod
    def init_parser(cls, parser, config=None):
        parser.add_argument('services', nargs='+', metavar='module[:service class]',
                            help='one or more dot path service classes to run')
        return parser

    @classmethod
    def print_hub_err(cls, config):
        return config.get(HUB_ERR_CONFIG_KEY, DEFAULT_HUB_ERR_PRINT) or DEFAULT_HUB_ERR_PRINT

    @classmethod
    def main(cls, args, config=None):
        eventlet.monkey_patch()
        hub_debug_mode = cls.print_hub_err(config)
        eventlet.debug.hub_exceptions(hub_debug_mode)
        eventlet.debug.hub_prevent_multiple_readers(False)
        services = []
        for path in args.services:
            msg = 'load service classes from {} failed, '
            err, srvs = find_services(path)
            log = False
            if err is not None:
                log = True
                msg += err
            if err is None and not srvs:
                log = True
                msg += 'No service classes'
            log and logger.warn(msg.format(path))
            services.extend(srvs)
        if not services:
            return
        start(services, config)
