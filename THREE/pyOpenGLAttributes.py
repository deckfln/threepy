"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""

import THREE.pyOpenGL as pyOpenGL
from OpenGL import *
from OpenGL_accelerate import *
from OpenGL.GL import *
from THREE.pyOpenGLObject import *


_conv = {
    'float32': GL_FLOAT,
    'float64': None,
    'uint16': GL_UNSIGNED_SHORT,
    'int16': GL_SHORT,
    'uint32': GL_UNSIGNED_INT,
    'int32': GL_INT,
    'uint8': GL_UNSIGNED_BYTE,
    'int8': GL_BYTE
}


class _pyOPenGLAattribute:
    def __init__(self, buffer, type, bytesPerElement, version):
        self.buffer = buffer
        self.type = type
        self.bytesPerElement = bytesPerElement
        self.version = version
        self.updated = False


class pyOpenGLAttributes(pyOpenGLObject):
    def __init__(self):
        self.buffers = {}

    def createBuffer(self, attribute, bufferType):
        array = attribute.array

        buffer = glGenBuffers(1)

        glBindBuffer(bufferType, buffer)
        if attribute.dynamic:
            pyOpenGL.OpenGL.glBufferData(bufferType, array.size * array.dtype.itemsize, array, GL_DYNAMIC_DRAW)
            # glBufferSubData(bufferType, 0, attribute.maxInstancedCount * attribute.itemSize * array.dtype.itemsize, array)
        else:
            pyOpenGL.OpenGL.glBufferData(bufferType, array.size * array.dtype.itemsize, array, GL_STATIC_DRAW)

        attribute.onUploadCallback()

        ta = array.dtype.name

        if ta not in _conv:
            raise RuntimeError("THREE.WebGLAttributes: Unsupported data buffer format %s" % ta)

        type = _conv[ta]
        if ta is None:
            raise RuntimeError('THREE.WebGLAttributes: Unsupported data buffer format: Float64Array.')

        return _pyOPenGLAattribute(buffer, type, array.dtype.itemsize, attribute.version)

    def updateBuffer(self, buffer, attribute, bufferType):
        array = attribute.array
        updateRange = attribute.updateRange

        glBindBuffer(bufferType, buffer)

        if not attribute.dynamic:
            glBufferData(bufferType, array, GL_STATIC_DRAW)
            return

        if updateRange.count < 0:
            if attribute.my_class(isInstancedBufferAttribute):
                # // Not using update ranges
                # pyOpenGL.OpenGL.glBufferData(bufferType, array.size * attribute.itemSize, None, GL_DYNAMIC_DRAW)
                pyOpenGL.OpenGL.glBufferSubData(bufferType, 0, attribute.maxInstancedCount * attribute.itemSize * array.itemsize, array)
            else:
                glBufferData(bufferType, array, GL_DYNAMIC_DRAW)
            return

        if updateRange.count > 0:
            glBufferSubData(bufferType, updateRange.offset * array.BYTES_PER_ELEMENT,
                            array.subarray(updateRange.offset, updateRange.offset + updateRange.count))

            updateRange.count = -1  # // reset range

            return

        raise RuntimeError('THREE.WebGLObjects.updateBuffer: dynamic THREE.BufferAttribute marked as needsUpdate but updateRange.count is 0, ensure you are using set methods or updating manually.')

    # //

    def get(self, attribute ):
        if attribute.my_class(isInterleavedBufferAttribute):
            attribute = attribute.data

        return self.buffers[attribute.uuid]

    def remove(self, attribute):
        if attribute.my_class(isInterleavedBufferAttribute):
            attribute = attribute.data

        if attribute.uuid in self.buffers:
            data = self.buffers[attribute.uuid]
            glDeleteBuffers(data.buffer)
            del self.buffers[attribute.uuid]

    def update(self, attribute, bufferType):
        if attribute.my_class(isInterleavedBufferAttribute):
            attribute = attribute.data

        if attribute.uuid in self.buffers:
            data = self.buffers[attribute.uuid]

            if data.version < attribute.version:
                self.updateBuffer(data.buffer, attribute, bufferType)
                data.version = attribute.version
                data.updated = True
            else:
                data.updated = False
        else:
            self.buffers[attribute.uuid] = self.createBuffer(attribute, bufferType)
            self.buffers[attribute.uuid].updated = True

        return self.buffers[attribute.uuid]
