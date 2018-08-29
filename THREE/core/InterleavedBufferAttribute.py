"""
/**
 * @author benaadams / https://twitter.com/ben_a_adams
 */
"""
import THREE._Math as _Math
from THREE.pyOpenGLObject import *


class InterleavedBufferAttribute(pyOpenGLObject):
    isInterleavedBufferAttribute = True
    
    def __init__(self, interleavedBuffer, itemSize, offset, normalized=False ):
        self.uuid = _Math.generateUUID()

        super().__init__()
        self.set_class(isInterleavedBufferAttribute)

        self.data = interleavedBuffer
        self.itemSize = itemSize
        self.offset = offset

        self.normalized = normalized

    def _getCount(self):
        return self.data.count

    def _getArray(self):
        return self.data.array

    count = property(_getCount)
    array = property(_getArray)

    def setX(self, index, x ):
        self.data.array[ index * self.data.stride + self.offset ] = x
        return self

    def setY(self, index, y ):
        self.data.array[ index * self.data.stride + self.offset + 1 ] = y
        return self

    def setZ(self, index, z ):
        self.data.array[ index * self.data.stride + self.offset + 2 ] = z
        return self

    def setW(self, index, w ):
        self.data.array[ index * self.data.stride + self.offset + 3 ] = w
        return self

    def getX(self, index ):
        return self.data.array[ index * self.data.stride + self.offset ]

    def getY(self, index ):
        return self.data.array[ index * self.data.stride + self.offset + 1 ]

    def getZ(self, index ):
        return self.data.array[ index * self.data.stride + self.offset + 2 ]

    def getW(self, index ):
        return self.data.array[ index * self.data.stride + self.offset + 3 ]

    def setXY(self, index, x, y ):
        index = index * self.data.stride + self.offset

        self.data.array[ index + 0 ] = x
        self.data.array[ index + 1 ] = y

        return self

    def setXYZ(self, index, x, y, z ):
        index = index * self.data.stride + self.offset

        self.data.array[ index + 0 ] = x
        self.data.array[ index + 1 ] = y
        self.data.array[ index + 2 ] = z

        return self

    def setXYZW(self, index, x, y, z, w ):
        index = index * self.data.stride + self.offset

        self.data.array[ index + 0 ] = x
        self.data.array[ index + 1 ] = y
        self.data.array[ index + 2 ] = z
        self.data.array[ index + 3 ] = w

        return self
