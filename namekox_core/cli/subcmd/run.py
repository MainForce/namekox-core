#! -*- coding: utf-8 -*-

# author: forcemain@163.com


from __future__ import print_function


import signal
import eventlet
import eventlet.debug
import logging.config


from functools import partial
from logging import getLogger
from namekox_core.core.service.runner import ServiceRunner
from namekox_core.core.service.discovery import find_services
from namekox_core.constants import LOGGING_CONFIG_KEY, DEFAULT_LOGGING_LEVEL, DEFAULT_LOGGING_FORMAT


from .base import BaseCommand


logger = getLogger(__name__)


def stop(runner, signum, frame):
    eventlet.spawn_n(runner.stop)


def start(services, config):
    runner = ServiceRunner(config)
    for service in services:
        runner.add_service(service)
    signal.signal(signal.SIGTERM, partial(stop, runner))
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
                            help='One or more dot path service classes to run')
        return parser

    @classmethod
    def main(cls, args, config=None):
        eventlet.monkey_patch()
        eventlet.debug.hub_exceptions(True)
        eventlet.debug.hub_prevent_multiple_readers(False)

        if LOGGING_CONFIG_KEY in config:
            logging.config.dictConfig(config[LOGGING_CONFIG_KEY])
        else:
            logging.basicConfig(level=DEFAULT_LOGGING_LEVEL, format=DEFAULT_LOGGING_FORMAT)
        services = []
        for path in args.services:
            msg = 'load service classes from {}'
            logger.debug(msg.format(path))
            err, srvs = find_services(path)
            log = False
            msg += ' failed, '
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
