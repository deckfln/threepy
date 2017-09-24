"""
/**
 * @author benaadams / https://twitter.com/ben_a_adams
 */
"""
import THREE._Math as _Math
from THREE.pyOpenGLObject import *
from THREE.BufferAttribute import *


class InterleavedBufferAttribute(pyOpenGLObject):
    isInterleavedBufferAttribute = True
    
    def __init__(self, interleavedBuffer, itemSize, offset, normalized ):
        self.uuid = _Math.generateUUID()

        self.data = interleavedBuffer
        self.itemSize = itemSize
        self.offset = offset

        self.normalized = normalized == True

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

"""
/**
 * @author benaadams / https://twitter.com/ben_a_adams
 */
"""


class _updateRange:
    def __init__(self, offset, count):
        self.offset = offset
        self.count = count


class InterleavedBuffer(pyOpenGLObject):
    isInterleavedBuffer = True
    
    def __init__(self, array=None, stride=None ):
        self.uuid = _Math.generateUUID()

        self.array = array
        self.stride = stride
        self.count = len(array) / stride if array is not None else 0

        self.dynamic = False
        self.updateRange = _updateRange(0, - 1)

        self.onUploadCallback = self._onUploadCallback

        self.version = 0

    def _onUploadCallback(self):
        return True

    def set(self, value ):
        if value == True:
            self.version += 1

    needsUpdate = property(None, set)    

    def setArray(self, array ):
        if isinstance(array, list):
            raise RuntimeError( 'THREE.BufferAttribute: array should be a Typed Array.' )

        self.count = len(array)/self.stride if array else 0
        self.array = array

    def setDynamic(self, value ):
        self.dynamic = value

        return self

    def copy(self, source ):
        self.array = source.array.constructor( source.array )
        self.count = source.count
        self.stride = source.stride
        self.dynamic = source.dynamic

        return self

    def copyAt(self, index1, attribute, index2 ):
        index1 *= self.stride
        index2 *= attribute.stride

        for i in range(self.stride):
            self.array[ index1 + i ] = attribute.array[ index2 + i ]

        return self

    def set(self, value, offset=0 ):
        self.array.set( value, offset )

        return self

    def clone(self):
        return type(self)().copy( self )

    def onUpload(self, callback ):
        self.onUploadCallback = callback
        return self

"""
/**
 * @author benaadams / https://twitter.com/ben_a_adams
 */
"""


class InstancedInterleavedBuffer(InterleavedBuffer):
    isInstancedInterleavedBuffer = True
    
    def __init__(self, array, stride, meshPerAttribute ):
        super().__init__(array, stride )

        self.meshPerAttribute = meshPerAttribute or 1


    def copy(self, source ):
        super().copy( source )

        self.meshPerAttribute = source.meshPerAttribute

        return self

"""
/**
 * @author benaadams / https://twitter.com/ben_a_adams
 */
"""


class InstancedBufferAttribute(BufferAttribute):
    isInstancedBufferAttribute = True
    
    def __init__(self, array, itemSize, meshPerAttribute ):
        super().__init__( array, itemSize )

        self.meshPerAttribute = meshPerAttribute or 1

    def copy(self, source ):
        super().copy( source )

        self.meshPerAttribute = source.meshPerAttribute

        return self
