"""
placeholder to simulate javascript feature like "isObject"
"""


class pyOpenGLObject:
    def __getattr__(self, item):
        if item[:2] == "is":
            return item in self.__dict__

        raise AttributeError("Missing attribute %s" % item)