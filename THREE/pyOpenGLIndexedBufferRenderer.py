"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from OpenGL_accelerate import *
from OpenGL.GL import *

from ctypes import c_void_p


class pyOpenGLIndexedBufferRenderer:
    def __init__( self, extensions, infoRender):
        self.mode = 0
        self._extensions = extensions
        self._infoRender = infoRender
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
        self._infoRender.calls += 1
        self._infoRender.vertices += count

        if self.mode == GL_TRIANGLES:
            self._infoRender.faces += count / 3
        elif self.mode == GL_POINTS:
            self._infoRender.points += count

    def renderInstances(self, geometry, start, count ):
        if not start:
            pointer = None
        else:
            pointer = c_void_p(start * self._bytesPerElement)
        glDrawElementsInstanced(self.mode, int(count), self._type, pointer, geometry.maxInstancedCount )

        self._infoRender.calls += 1
        self._infoRender.vertices += count * geometry.maxInstancedCount

        if self.mode == GL_TRIANGLES:
            self._infoRender.faces += geometry.maxInstancedCount * count / 3
        elif self.mode == GL_POINTS:
            self._infoRender.points += geometry.maxInstancedCount * count
