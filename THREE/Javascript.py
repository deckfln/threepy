"""
Simulate a javascript object behaviour
"""


class javascriptObject:
    def __init__(self, source=None):
        if not source:
            return

        for k in source.keys():
            v = source[k]
            if isinstance(v, str):
                value = v
            elif isinstance(v, int):
                value = v
            elif isinstance(v, float):
                value = v
            elif isinstance(v, dict):
                value = javascriptObject(v)
            else:
                value = v

            self.__setattr__(k, value)

    def __getattr__(self, item):
        if item not in self.__dict__:
            return None

        return self.__dict__[item]

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, item, v):
        if item not in self.__dict__:
            if isinstance(v, str):
                value = v
            elif isinstance(v, int):
                value = v
            elif isinstance(v, float):
                value = v
            elif isinstance(v, dict):
                value = javascriptObject(v)
            else:
                value = v
            self.__setattr__(item, value)
        else:
            self.__dict__[item] = v

    def __iter__(self):
        return iter(self.__dict__)