#! -*- coding: utf-8 -*-

# author: forcemain@163.com


from logging import getLogger
from namekox_core.constants import TPLREPO_CONFIG_KEY, DEFAULT_TPLREPO_URL


from .base import BaseCommand


logger = getLogger(__name__)


class Create(BaseCommand):
    """ create micro services """
    @classmethod
    def name(cls):
        return 'create'

    @classmethod
    def init_parser(cls, parser, config=None):
        parser.add_argument('services', nargs='+', metavar='service names',
                            help='one or more micro services to create')
        return parser

    @classmethod
    def main(cls, args, config=None):
        from git import Repo
        repourl = config.get(TPLREPO_CONFIG_KEY, DEFAULT_TPLREPO_URL) or DEFAULT_TPLREPO_URL
        for name in args.services:
            msg = 'starting git clone from {} to {}'
            logger.debug(msg)
            Repo.clone_from(repourl, name, branch='master')
        msg = 'micro services {} created'.format(args.services)
        logger.debug(msg)
