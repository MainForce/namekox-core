#! -*- coding: utf-8 -*-

# author: forcemain@163.com

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class BaseCommand(object):
    @classmethod
    @abc.abstractmethod
    def name(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def init_parser(cls, parser, config=None):
        pass

    @classmethod
    @abc.abstractmethod
    def main(cls, args, config=None):
        pass
