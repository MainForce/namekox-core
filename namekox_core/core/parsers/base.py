#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import os


from .patterns import *


def recursive_replace_env_var(match):
    var, default = match.groups()
    result = os.environ.get(var, None) or default or ''
    while IMPLICIT_ENV_VAR_MATCHER.match(result):
        result = ENV_VAR_MATCHER.sub(recursive_replace_env_var, result)
    return result
