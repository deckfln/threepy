"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""

from OpenGL import *
# from OpenGL_accelerate import *
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
    def __init__(self, buffer, type, bytesPerElement, version, parent_uuid):
        self.buffer = buffer
        self.type = type
        self.bytesPerElement = bytesPerElement
        self.version = version
        self.updated = False
        self.references = {parent_uuid: True}


class pyOpenGLAttributes(pyOpenGLObject):
    def __init__(self):
        self.buffers = {}

    def createBuffer(self, attribute, bufferType, parent_uuid):
        array = attribute.array

        buffer = glGenBuffers(1)

        glBindBuffer(bufferType, buffer)
        if attribute.dynamic:
            OpenGL.raw.GL.VERSION.GL_1_5.glBufferData(bufferType, array.size * array.dtype.itemsize, array, GL_DYNAMIC_DRAW)
            # glBufferSubData(bufferType, 0, attribute.maxInstancedCount * attribute.itemSize * array.dtype.itemsize, array)
        else:
            OpenGL.raw.GL.VERSION.GL_1_5.glBufferData(bufferType, array.size * array.dtype.itemsize, array, GL_STATIC_DRAW)

        attribute.onUploadCallback()

        ta = array.dtype.name

        if ta not in _conv:
            raise RuntimeError("THREE.WebGLAttributes: Unsupported data buffer format %s" % ta)

        type = _conv[ta]
        if ta is None:
            raise RuntimeError('THREE.WebGLAttributes: Unsupported data buffer format: Float64Array.')

        return _pyOPenGLAattribute(buffer, type, array.dtype.itemsize, attribute.version, parent_uuid)

    def updateBuffer(self, buffer, attribute, bufferType):
        array = attribute.array
        updateRange = attribute.updateRange

        glBindBuffer(bufferType, buffer)

        if not attribute.dynamic:
            glBufferData(bufferType, array, GL_STATIC_DRAW)
            return

        count = updateRange.count
        if count < 0:
            if attribute.my_class(isInstancedBufferAttribute):
                # // Not using update ranges
                # pyOpenGL.OpenGL.glBufferData(bufferType, array.size * attribute.itemSize, None, GL_DYNAMIC_DRAW)
                OpenGL.raw.GL.VERSION.GL_1_5.glBufferSubData(bufferType, 0, attribute.maxInstancedCount * attribute.itemSize * array.itemsize, array)
            else:
                glBufferData(bufferType, array, GL_DYNAMIC_DRAW)
            return

        if count > 0:
            OpenGL.raw.GL.VERSION.GL_1_5.glBufferSubData(bufferType,
                                                         updateRange.offset * attribute.itemSize * array.itemsize,
                                                         attribute.maxInstancedCount * attribute.itemSize * array.itemsize,
                                                         array)

            #OpenGL.raw.GL.VERSION.GL_1_5.glBufferSubData(bufferType, updateRange.offset * array.dtype.itemsize,
            #                array[updateRange.offset:updateRange.offset + count])

            updateRange.count = -1  # // reset range

            return

        raise RuntimeError('THREE.WebGLObjects.updateBuffer: dynamic THREE.BufferAttribute marked as needsUpdate but updateRange.count is 0, ensure you are using set methods or updating manually.')

    # //

    def get(self, attribute ):
        if attribute.my_class(isInterleavedBufferAttribute):
            attribute = attribute.data

        return self.buffers[attribute.uuid] if attribute.uuid in self.buffers else None

    def __del__(self):
        self.dispose()

    def dispose(self, attribute=None, parent=None):
        if attribute is None:
            # delete all attributes
            for data in self.buffers.values():
                print("glDeleteBuffers(1, [data.buffer])")
            return

        if attribute.my_class(isInterleavedBufferAttribute):
            attribute = attribute.data

        if attribute.uuid in self.buffers:
            data = self.buffers[attribute.uuid]
            parent_uuid = parent.uuid
            if parent_uuid in data.references:
                del data.references[parent_uuid]

                if len(data.references) == 0:
                    glDeleteBuffers(1, [data.buffer])
                    del self.buffers[attribute.uuid]

    def update(self, attribute, bufferType, parent):
        if attribute.my_class(isInterleavedBufferAttribute):
            attribute = attribute.data

        uuid = attribute.uuid
        parent_uuid = parent.uuid

        if attribute.uuid in self.buffers:
            data = self.buffers[attribute.uuid]

            if parent_uuid not in data.references:
                data.references[parent_uuid] = True

            if data.version < attribute.version:
                self.updateBuffer(data.buffer, attribute, bufferType)
                data.version = attribute.version
                data.updated = True
            else:
                data.updated = False
        else:
            self.buffers[uuid] = self.createBuffer(attribute, bufferType, parent_uuid)
            self.buffers[uuid].updated = True

        return self.buffers[attribute.uuid]
