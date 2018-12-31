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
        self.openglFrameBuffer = None
        self.openglDepthBuffer = None
        self.version = -1
        self.clippingState = None
        self.imageopenglTextureCube = None
        self.image_powerof2 = None
        self.lightsHash = None
        self._maxMipLevel = 0


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
        del property.object

        del self.properties[object.uuid]

    def clear(self):
        self.properties = {}
