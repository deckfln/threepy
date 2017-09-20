"""
placeholder to simulate javascript feature like "isObject"
"""


class RootObject:
    def __getattr__(self, item):
        if hasattr(self, item):
            return self.item

        return None
