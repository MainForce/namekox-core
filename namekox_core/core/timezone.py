#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import pytz


# By design, these four functions don't perform any checks on their arguments.
# The caller should ensure that they don't receive an invalid value like None.


def is_naive(dt):
    """ not timezone """
    return dt.utcoffset() is None


def is_aware(dt):
    """ has timezone """
    return dt.utcoffset() is not None


def make_aware(dt, tz=pytz.UTC):
    return dt.replace(tzinfo=tz)


def make_naive(dt, tz=pytz.UTC):
    return dt.astimezone(tz).replace(tzinfo=None)
