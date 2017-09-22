"""
Simulate a javascript object behaviour
"""


class javascriptObject:
    def __init__(self, source):
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

    def __iter__(self):
        return iter(self.__dict__)


