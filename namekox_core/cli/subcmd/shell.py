#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import sys
import logging


from types import ModuleType
from logging import getLogger
from namekox_core.constants import CONTEXT_CONFIG_KEY
from namekox_core.core.loaders import import_dotpath_class
from namekox_core.constants import DEFAULT_LOGGING_LEVEL, DEFAULT_LOGGING_FORMAT


from .base import BaseCommand


logger = getLogger(__name__)


class ShellRunner(object):
    shell_default = 'python'
    shells = ['ipython', shell_default]

    def __init__(self, banner='', context=None):
        self.banner = banner
        self.context = context or {}

    def ipython(self):
        from IPython import embed
        return embed(banner1=self.banner, user_ns=self.context)

    def python(self):
        from code import interact as embed
        return embed(banner=self.banner, local=self.context)

    def start_shell(self, shell):
        if not sys.stdin.isatty():
            available_shells = [self.shell_default]
        else:
            available_shells = [shell, self.shell_default] if shell else self.shells
        for shell in available_shells:
            try:
                return getattr(self, shell)()
            except ImportError:
                pass
        return


class Shell(BaseCommand):
    """ launch an interactive shell """
    @classmethod
    def name(cls):
        return 'shell'

    @classmethod
    def init_parser(cls, parser, config=None):
        parser.add_argument('-s', '--shell', action='store',
                            choices=ShellRunner.shells,
                            help='Specify an interactive shell')
        return parser

    @classmethod
    def init_context(cls, config):
        module = ModuleType('namekox')
        for ctx_cls_path in config.get(CONTEXT_CONFIG_KEY, []):
            msg = 'load context objects from {}'
            logger.debug(msg.format(ctx_cls_path))
            err, ctx_cls = import_dotpath_class(ctx_cls_path)
            log = False
            msg += 'failed, '
            if err is not None:
                log = True
                msg += err
            log and logger.warn(msg.format(ctx_cls_path))
            if ctx_cls is None:
                continue
            ctx_obj = ctx_cls(config)
            setattr(module, ctx_obj.name(), ctx_obj)
        return module

    @classmethod
    def main(cls, args, config=None):
        logging.basicConfig(level=DEFAULT_LOGGING_LEVEL, format=DEFAULT_LOGGING_FORMAT)
        
        banner = 'Namekox Python {} shell on {}'.format(sys.version, sys.platform)
        runner = ShellRunner(banner, {'nx': cls.init_context(config)})
        runner.start_shell(shell=args.shell)
