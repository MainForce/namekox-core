#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


from logging import getLogger


from namekox_core.core.spawning import SpawningProxy


from .container import get_container_cls


logger = getLogger(__name__)


class ServiceRunner(object):
    def __init__(self, config):
        self.config = config

        self.container_map = {}
        self.container_cls = get_container_cls(config)

    @property
    def service_names(self):
        return list(self.container_map.keys())

    @property
    def containers(self):
        return list(self.container_map.values())

    def add_service(self, cls):
        container = self.container_cls(cls, self.config)
        self.container_map[cls.name] = container

    def start(self):
        logger.debug('starting services {}'.format(self.service_names))

        SpawningProxy(self.containers).start()

        logger.debug('services {} started'.format(self.service_names))

    def stop(self):
        logger.debug('stopping services {}'.format(self.service_names))

        SpawningProxy(self.containers).stop()

        logger.debug('services {} stopped'.format(self.service_names))

    def kill(self):
        logger.debug('killing services {}'.format(self.service_names))

        SpawningProxy(self.containers).kill()

        logger.debug('services {} killed'.format(self.service_names))

    def wait(self):
        SpawningProxy(self.containers).wait()
