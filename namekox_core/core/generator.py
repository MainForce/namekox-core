#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import os
import uuid
import hashlib


def generator_md5(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def generator_uuid(length=16):
    return str(uuid.UUID(bytes=os.urandom(length), version=4))
