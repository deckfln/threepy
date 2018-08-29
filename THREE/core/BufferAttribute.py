"""
    /**
     * @author mrdoob / http://mrdoob.com/
     */
"""
import THREE._Math as _Math
from THREE.math.Color import *
from THREE.math.Vector2 import *
from THREE.math.Vector3 import *
from THREE.math.Vector4 import *
from THREE.pyOpenGLObject import *

import numpy as np


class _updateRange:
    def __init__(self, offset, count):
        self.offset = offset
        self.count = count


class BufferAttribute(pyOpenGLObject):
    isBufferAttribute = True

    def __init__(self, array, itemSize=0, normalized=False):
        if isinstance(array, list):
            print('THREE.BufferAttribute: array should be a Typed Array.')

        super().__init__()
        self.set_class(isBufferAttribute)

        self.uuid = _Math.generateUUID()
        self.name = ''

        self.array = array
        self.itemSize = itemSize
        self.count = 0
        if array is not None:
            self.count = int(len(array) / itemSize)
        self.normalized = normalized

        self.dynamic = False
        self.updateRange = _updateRange(0, - 1)

        self.version = 0
        # self.needsUpdate = False

    def setUpdate(self, value):
        if value:
            self.version += 1

    needsUpdate = property(None, setUpdate)    

    def onUploadCallback(self):
        return True

    def onUpload(self, callback):
        self.onUploadCalback =callback

    def setArray(self, array):
        if isinstance(array, list):
            print('THREE.BufferAttribute: array should be a Typed Array.')

        self.count = 0
        if array is not None:
            self.count = len(array) / self.itemSize
        self.array = array

        return self

    def setDynamic(self, value):
        self.dynamic = value

        return self

    def copy(self, source):
        self.name = source.name
        self.array[:] = source.array[:]
        self.itemSize = source.itemSize
        self.count = source.count
        self.normalized = source.normalized

        self.dynamic = source.dynamic

        return self

    def copyAt(self, index1, attribute, index2):
        index1 *= self.itemSize
        index2 *= attribute.itemSize

        for i in range(self.itemSize):
            self.array[index1 + i] = attribute.array[index2 + i]

        return self

    def copyArray(self, array):
        self.array.set(array)

        return self

    def copyColorsArray(self, colors):
        array = self.array
        offset = 0

        for color in colors:
            if color is None:
                print('THREE.BufferAttribute.copyColorsArray(): color is undefined')
                color = Color()

            array[offset] = color.r
            array[offset + 1] = color.g
            array[offset + 2] = color.b
            offset += 3
            
        return self

    def copyVector2sArray(self, vectors):
        array = self.array
        offset = 0

        for vector in vectors:
            if vector is None:
                print('THREE.BufferAttribute.copyVector2sArray(): vector is undefined')
                vector = Vector2()

            array[offset] = vector.x
            array[offset + 1] = vector.y
            offset += 2

        return self

    def copyVector3sArray(self, vectors):
        array = self.array
        offset = 0

        for vector in vectors:
            if vector is None:
                print('THREE.BufferAttribute.copyVector3sArray(): vector is undefined')
                vector = Vector3()
            array[offset] = vector.np[0]
            array[offset + 1] = vector.np[1]
            array[offset + 2] = vector.np[2]
            offset += 3
        return self

    def copyVector4sArray(self, vectors):
        array = self.array
        offset = 0

        for vector in vectors:
            if vector is None:
                print('THREE.BufferAttribute.copyVector4sArray(): vector is undefined')
                vector = Vector4()

            array[offset] = vector.x
            array[offset + 1] = vector.y
            array[offset + 2] = vector.z
            array[offset + 3] = vector.w
            offset += 4

        return self

    def set(self, value, offset=0):
        self.array[offset:offset+len(value)] = value
        return self

    def getX(self, index):
        return self.array[index * self.itemSize]

    def setX(self, index, x):
        self.array[index * self.itemSize] = x

        return self

    def getY(self, index):
        return self.array[index * self.itemSize + 1]

    def setY(self, index, y):
        self.array[index * self.itemSize + 1] = y

        return self

    def getZ(self, index):
        return self.array[index * self.itemSize + 2]

    def setZ(self, index, z):
        self.array[index * self.itemSize + 2] = z

        return self

    def getW(self, index):
        return self.array[index * self.itemSize + 3]

    def setW(self, index, w):
        self.array[index * self.itemSize + 3] = w

        return self

    def setXY(self, index, x, y):
        index *= self.itemSize

        self.array[index + 0] = x
        self.array[index + 1] = y

        return self

    def setXYZ(self, index, x, y, z):
        index *= self.itemSize

        self.array[index + 0] = x
        self.array[index + 1] = y
        self.array[index + 2] = z

        return self

    def setXYZW(self, index, x, y, z, w):
        index *= self.itemSize

        self.array[index + 0] = x
        self.array[index + 1] = y
        self.array[index + 2] = z
        self.array[index + 3] = w
        return self

    def clone(self):
        return type(self)(self.array, self.itemSize).copy(self)

        
class Int8BufferAttribute(BufferAttribute):
    def __init__(self, arrayx, itemSize, normalized=False):
        if isinstance(arrayx, list):
            super().__init__(np.array(arrayx, 'b'), itemSize, normalized)
        else:
            super().__init__(np.zeros(arrayx, 'b').shape, itemSize, normalized)


class Uint8BufferAttribute(BufferAttribute):
    def __init__(self, arrayx, itemSize, normalized=False):
        if isinstance(arrayx, list):
            super().__init__(np.array(arrayx, 'B'), itemSize, normalized)
        else:
            super().__init__(np.zeros(arrayx, 'B').shape, itemSize, normalized)


class Uint8ClampedBufferAttribute(BufferAttribute):
    def __init__(self,  arrayx, itemSize, normalized=False):
        if isinstance(arrayx, list):
            super().__init__(np.array(arrayx, 'B'), itemSize, normalized)
        else:
            super().__init__(np.zeros(arrayx.shape, 'B'), itemSize, normalized)


class Int16BufferAttribute(BufferAttribute):
    def __init__(self, arrayx, itemSize, normalized=False):
        if isinstance(arrayx, list):
            super().__init__(np.array(arrayx, 'l'), itemSize, normalized)
        else:
            super().__init__(np.zeros(arrayx.shape, 'l'), itemSize, normalized)


class Uint16BufferAttribute(BufferAttribute):
    def __init__(self, arrayx, itemSize, normalized=False):
        if isinstance(arrayx, list):
            super().__init__(np.array(arrayx, 'L'), itemSize, normalized)
        else:
            super().__init__(np.zeros(arrayx.shape, 'L'), itemSize, normalized)


class Int32BufferAttribute(BufferAttribute):
    def __init__(self, arrayx, itemSize, normalized=False):
        if isinstance(arrayx, list):
            super().__init__(np.array(arrayx, dtype=np.int32), itemSize, normalized)
        else:
            super().__init__(np.zeros(arrayx.shape, dtype=np.int32), itemSize, normalized)


class Uint32BufferAttribute(BufferAttribute):
    def __init__(self, arrayx, itemSize, normalized=False):
        if isinstance(arrayx, list):
            super().__init__(np.array(arrayx, dtype=np.uint32), itemSize, normalized)
        else:
            super().__init__(np.zeros(arrayx.shape, dtype=np.uint32), itemSize, normalized)


class Float32BufferAttribute(BufferAttribute):
    def __init__(self, arrayx, itemSize, normalized=False):
        if isinstance(arrayx, list):
            super().__init__(np.array(arrayx, dtype=np.float32), itemSize, normalized)
        elif isinstance(arrayx, int):
            super().__init__(np.zeros(arrayx, dtype=np.float32), itemSize, normalized)
        else:
            a = np.zeros(arrayx.shape, dtype=np.float32)
            super().__init__(a, itemSize)


class Float64BufferAttribute(BufferAttribute):
    def __init__(self, arrayx, itemSize, normalized=False):
        if isinstance(arrayx, list):
            super().__init__(np.array(arrayx, 'd'), itemSize, normalized)
        else:
            super().__init__(np.zeros(arrayx.shape, 'd'), itemSize, normalized)
