"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.pyOpenGLObject import *
from THREE.renderers.pyOpenGL.pyOpenGLInfo import *
from THREE.renderers.pyOpenGL.pyOpenGLCapabilities import *


class pyOpenGLBufferRenderer:
    def __init__( self, extensions, info: pyOpenGLInfo, capbilities: pyOpenGLCapabilities):
        self.mode = 0
        self.info = info
        self.extensions = extensions
        
    def setMode(self, value):
        self.mode = value

    def render(self, start, count):
        glDrawArrays( self.mode, int(start), int(count))

        self.info.update(count, self.mode)

    def renderInstances(self, geometry, start, count):
        position = geometry.attributes.position

        if position.my_class(isInterleavedBufferAttribute):
            count = position.data.count
            glDrawArraysInstanced(self.mode, 0, count, geometry.maxInstancedCount)
        else:
            glDrawArraysInstanced(self.mode, start, count, geometry.maxInstancedCount)

        self.info.update(count, self.mode, geometry.maxInstancedCount)
