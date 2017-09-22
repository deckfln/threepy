"""
/**
 * @author fordacious / fordacious.github.io
 */
"""


class _map:
    def __init__(self):
        self.program = None
        self.shader = None
        self.numClippingPlanes = 0
        self.numIntersection = 0
        self.openglTexture = None
        self.openglInit = False
        self.currentAnisotropy = False
        self.version = -1


class pyOpenGLProperties:
    def __init__(self):
        self.properties = {}

    def get(self, object ):
        uuid = object.uuid
        if uuid in self.properties:
            return self.properties[ uuid ]

        map = _map()
        self.properties[ uuid ] = map

        return map

    def remove(self, object ):
        del self.properties[ object.uuid ]

    def clear(self):
        self.properties = {}
