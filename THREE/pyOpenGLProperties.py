"""
/**
 * @author fordacious / fordacious.github.io
 */
"""


class _map:
    def __init__(self, object):
        self.object = object
        self.program = None
        self.shader = None
        self.numClippingPlanes = 0
        self.numIntersection = 0
        self.openglTexture = None
        self.openglInit = False
        self.currentAnisotropy = False
        self.frameBuffer = None
        self.depthBuffer = None
        self.version = -1
        self.clippingState = None
        self.imageopenglTextureCube = None
        self.image_powerof2 = None


# global clean up
dispose_queue = []


class pyOpenGLProperties:
    def __init__(self):
        self.properties = {}

    def get(self, object ):
        uuid = object.uuid
        if uuid in self.properties:
            return self.properties[ uuid ]

        map = _map(object)
        self.properties[ uuid ] = map

        return map

    def remove(self, object):
        property = self.properties[object.uuid]
        property.object.dispose()

        del self.properties[object.uuid]

    def clear(self):
        self.properties = {}
