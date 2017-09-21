"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from OpenGL.GL import *

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


class pyOpenGLAttributes:
    def __init__(self):
        self.buffers = {}

    def createBuffer(self, attribute, bufferType):
        array = attribute.array
        usage = GL_DYNAMIC_DRAW if attribute.dynamic else GL_STATIC_DRAW

        buffer = glGenBuffers(1)

        glBindBuffer(bufferType, buffer)
        glBufferData(bufferType, array, usage)

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
        elif updateRange.count == - 1:
            # // Not using update ranges
            glBufferSubData(bufferType, 0, array)
        elif updateRange.count == 0:
            raise RuntimeError('THREE.WebGLObjects.updateBuffer: dynamic THREE.BufferAttribute marked as needsUpdate but updateRange.count is 0, ensure you are using set methods or updating manually.')
        else:
            glBufferSubData(bufferType, updateRange.offset * array.BYTES_PER_ELEMENT,
                array.subarray(updateRange.offset, updateRange.offset + updateRange.count))

            updateRange.count = -1  # // reset range

    # //

    def get(self, attribute ):
        if hasattr(attribute, 'isInterleavedBufferAttribute'):
            attribute = attribute.data

        return self.buffers[attribute.uuid]

    def remove(self, attribute):
        if hasattr(attribute, 'isInterleavedBufferAttribute'):
            attribute = attribute.data

        if attribute.uuid in self.buffers:
            data = self.buffers[attribute.uuid]
            glDeleteBuffers(data.buffer)
            del self.buffers[attribute.uuid]

    def update(self, attribute, bufferType):
        if hasattr(attribute, 'isInterleavedBufferAttribute'):
            attribute = attribute.data

        if attribute.uuid in self.buffers:
            data = self.buffers[attribute.uuid]

            if data.version < attribute.version:
                self.updateBuffer(data.buffer, attribute, bufferType)
                data.version = attribute.version
        else:
            self.buffers[attribute.uuid] = self.createBuffer(attribute, bufferType)

        return self.buffers[attribute.uuid]
