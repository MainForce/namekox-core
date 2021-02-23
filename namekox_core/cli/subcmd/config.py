#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import yaml


from .base import BaseCommand


class Config(BaseCommand):
    """ show yaml string config """
    @classmethod
    def name(cls):
        return 'config'

    @classmethod
    def init_parser(cls, parser, config=None):
        return parser

    @classmethod
    def main(cls, args, config=None):
        print('' if not config else yaml.dump(config))
