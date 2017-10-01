"""
placeholder to simulate javascript feature like "isObject"
"""
from numba import *


class pyOpenGLObject:
    def __getattr__(self, item):
        if item[:2] == "is":
            return item in self.__dict__

        raise AttributeError("Missing attribute %s" % item)