"""
placeholder to simulate javascript feature like "isObject"
"""


class RootObject:
    def __getattr__(self, item):
        if item[:2] == 'is':
            if hasattr(self, item):
                return self.item
            else:
                return False
        else:
            raise AttributeError("Missing attribute %s" % item)