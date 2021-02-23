#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import os
import uuid
import socket
import hashlib
import contextlib


def generator_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with contextlib.closing(s) as sock:
        sock.bind(('', 0))
        _, port = sock.getsockname()
    return int(port)


def generator_md5(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def generator_uuid(length=16):
    return str(uuid.UUID(bytes=os.urandom(length), version=4))
