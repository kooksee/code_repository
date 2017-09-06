# -*- coding: utf-8 -*-

class Hello(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        print args, kwargs
        pass
