#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import print_function
from __future__ import unicode_literals


import os
import sys
import yaml
import argparse
import logging.config


from functools import partial
from logging import getLogger
from pkg_resources import get_distribution
from namekox_core.constants import COMMAND_CONFIG_KEY
from namekox_core.core.loaders import import_dotpath_class
from namekox_core.core.parsers.base import recursive_replace_env_var
from namekox_core.core.parsers.patterns import ENV_VAR_MATCHER, IMPLICIT_ENV_VAR_MATCHER
from namekox_core.constants import LOGGING_CONFIG_KEY, DEFAULT_LOGGING_LEVEL, DEFAULT_LOGGING_FORMAT


from .subcmd.base import BaseCommand


logger = getLogger(__name__)


DEFAULT_COMMANDS = [
    'namekox_core.cli.subcmd.run:Run',
    'namekox_core.cli.subcmd.shell:Shell',
    'namekox_core.cli.subcmd.config:Config',
    'namekox_core.cli.subcmd.create:Create',
]


def env_var_constructor(loader, node, raw=False):
    raw_value = loader.construct_scalar(node)
    value = ENV_VAR_MATCHER.sub(recursive_replace_env_var, raw_value)
    return value if raw else yaml.safe_load(value)


def setup_yaml_parser():
    yaml.add_implicit_resolver(
        '!env_var', IMPLICIT_ENV_VAR_MATCHER, Loader=yaml.UnsafeLoader
    )
    yaml.add_constructor(
        '!env_var', env_var_constructor, Loader=yaml.UnsafeLoader
    )
    yaml.add_constructor(
        '!raw_env_var', partial(env_var_constructor, raw=True), yaml.UnsafeLoader
    )


def get_cfg_from_yaml(f):
    if not os.path.exists(f) or not os.path.isfile(f):
        data = {}
    else:
        fobj = open(f, 'rb')
        data = yaml.unsafe_load(fobj) or {}
        fobj.close()
    return data


def set_log_from_conf(c):
    if LOGGING_CONFIG_KEY in c:
        logging.config.dictConfig(c[LOGGING_CONFIG_KEY])
    else:
        logging.basicConfig(level=DEFAULT_LOGGING_LEVEL, format=DEFAULT_LOGGING_FORMAT)


def get_cmd_from_conf(c):
    set_log_from_conf(c)
    cmds = set(c.get(COMMAND_CONFIG_KEY, []))
    cmds.update(DEFAULT_COMMANDS)
    return [(cmd, import_dotpath_class(cmd)) for cmd in cmds]


def setup_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version',
                        version=get_distribution('namekox_core').version)
    config_file = os.path.join('.', 'config.yaml')
    config_data = get_cfg_from_yaml(config_file)
    sub_command = get_cmd_from_conf(config_data)
    sub_parsers = parser.add_subparsers()
    for cls, res in sub_command:
        err, cmd = res
        msg = 'load command classes from {} failed, '.format(cls)
        if err is not None or cmd is None:
            msg += err
            logger.warn(msg)
            continue
        if not issubclass(cmd, BaseCommand):
            msg += 'no subclass of BaseCommand'
            logger.warn(msg)
            continue
        cmd_parser = sub_parsers.add_parser(
            cmd.name(), help=cmd.__doc__, description=cmd.__doc__)
        cmd_runner = partial(cmd.main, config=config_data)
        cmd_parser.set_defaults(main=cmd_runner)
        cmd.init_parser(cmd_parser, config=config_data)
    return parser


def main():
    setup_yaml_parser()
    if '.' not in sys.path:
        sys.path.insert(0, '.')
    parser = setup_args_parser()
    result = parser.parse_args()
    result.main(result)
