#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import logging


HUB_ERR_CONFIG_KEY = 'HUB_ERR'
DEFAULT_HUB_ERR_PRINT = False


CONTEXT_CONFIG_KEY = 'CONTEXT'


COMMAND_CONFIG_KEY = 'COMMAND'


SERVICE_CONFIG_KEY = 'SERVICE'


WORKERS_CONFIG_KEY = 'WORKERS'
DEFAULT_WORKERS_NUMBER = 1000


LOGGING_CONFIG_KEY = 'LOGGING'
DEFAULT_LOGGING_LEVEL = logging.DEBUG
DEFAULT_LOGGING_FORMAT = '%(asctime)s %(levelname)s %(message)s'


TPLREPO_CONFIG_KEY = 'TPLREPO'
DEFAULT_TPLREPO_URL = 'https://github.com/namekox-org/service-template.git'
