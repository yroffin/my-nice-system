#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def singleton(class_):
    """singleton decorator
    """

    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance