#! -*- coding: utf-8 -*-

# author: forcemain@163.com


import os
import uuid


def generator_uuid(length=16):
    return str(uuid.UUID(bytes=os.urandom(length), version=4))

