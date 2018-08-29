"""
/**
 * @author benaadams / https://twitter.com/ben_a_adams
 */
"""
from THREE.pyOpenGLObject import *
import THREE._Math


class _updateRange:
    def __init__(self, offset, count):
        self.offset = offset
        self.count = count


class InterleavedBuffer(pyOpenGLObject):
    isInterleavedBuffer = True

    def __init__(self, array=None, stride=None):
        super().__init__()
        self.uuid = _Math.generateUUID()
        self.set_class(isInterleavedBuffer)
        self.array = array
        self.stride = stride
        self.count = len(array) / stride if array is not None else 0

        self.dynamic = False
        self.updateRange = _updateRange(0, - 1)

        self.onUploadCallback = self._onUploadCallback

        self.version = 0

    def _onUploadCallback(self):
        return True

    def set(self, value):
        if value:
            self.version += 1

    needsUpdate = property(None, set)

    def setArray(self, array):
        if isinstance(array, list):
            raise RuntimeError('THREE.BufferAttribute: array should be a Typed Array.')

        self.count = len(array) / self.stride if array else 0
        self.array = array

    def setDynamic(self, value):
        self.dynamic = value

        return self

    def copy(self, source):
        self.array = source.array.constructor(source.array)
        self.count = source.count
        self.stride = source.stride
        self.dynamic = source.dynamic

        return self

    def copyAt(self, index1, attribute, index2):
        index1 *= self.stride
        index2 *= attribute.stride

        for i in range(self.stride):
            self.array[index1 + i] = attribute.array[index2 + i]

        return self

    def set(self, value, offset=0):
        self.array.set(value, offset)

        return self

    def clone(self):
        return type(self)().copy(self)

    def onUpload(self, callback):
        self.onUploadCallback = callback
        return self
