"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from OpenGL_accelerate import *
from OpenGL.GL import *

from ctypes import c_void_p


class pyOpenGLIndexedBufferRenderer:
    def __init__( self, extensions, info):
        self.mode = 0
        self._extensions = extensions
        self.info = info
        self._type = 0
        self._bytesPerElement = 0

    def setMode(self, value):
        self.mode = value

    def setIndex(self, value):
        self._type = value.type
        self._bytesPerElement = value.bytesPerElement

    def render(self, start, count):
        if not start:
            pointer = None
        else:
            pointer = int(start * self._bytesPerElement)

        try:
            glDrawElements(self.mode, int(count), self._type, pointer)
        except:
            print("down")

        self.info.update(count, self.mode)

    def renderInstances(self, geometry, start, count ):
        if not start:
            pointer = None
        else:
            pointer = c_void_p(start * self._bytesPerElement)
        glDrawElementsInstanced(self.mode, int(count), self._type, pointer, geometry.maxInstancedCount )

        self.info.update(count, self.mode, geometry.maxInstancedCount)
