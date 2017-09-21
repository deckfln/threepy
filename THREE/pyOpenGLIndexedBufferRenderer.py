"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
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
        glDrawElements(self.mode, int(count), self._type, c_void_p(start * self._bytesPerElement))

        self._infoRender.calls += 1
        self._infoRender.vertices += count

        if self.mode == GL_TRIANGLES:
            self._infoRender.faces += count / 3
        elif self.mode == GL_POINTS:
            self._infoRender.points += count

    def renderInstances(self, geometry, start, count ):
        extension = self._extensions.get( 'ANGLE_instanced_arrays' )

        if extension is None:
            raise RuntimeError( 'THREE.WebGLIndexedBufferRenderer: using THREE.InstancedBufferGeometry but hardware does not support extension ANGLE_instanced_arrays.' );

        extension.drawElementsInstancedANGLE(self.mode, int(count), c_void_p(self._type, start * self.bytesPerElement), geometry.maxInstancedCount )

        self._infoRender.calls += 1
        self._infoRender.vertices += count * geometry.maxInstancedCount

        if self.mode == GL_TRIANGLES:
            self._infoRender.faces += geometry.maxInstancedCount * count / 3
        elif self.mode == GL_POINTS:
            self._infoRender.points += geometry.maxInstancedCount * count
