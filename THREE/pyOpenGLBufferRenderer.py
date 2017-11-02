"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from OpenGL.GL import *


class pyOpenGLBufferRenderer:
    def __init__( self, extensions, infoRender ):
        self.mode = 0
        self.infoRender = infoRender
        self.extensions = extensions
        
    def setMode(self, value ):
        self.mode = value

    def render(self, start, count ):
        glDrawArrays( self.mode, int(start), int(count) )

        self.infoRender.calls += 1
        self.infoRender.vertices += count

        if self.mode == GL_TRIANGLES:
            self.infoRender.faces += count / 3
        elif self.mode == GL_POINTS:
            self.infoRender.points += count

    def renderInstances(self, geometry, start, count ):
        extension = self.extensions.get( 'ANGLE_instanced_arrays' )

        if extension is None:
            raise RuntimeError( 'THREE.WebGLBufferRenderer: using THREE.InstancedBufferGeometry but hardware does not support extension ANGLE_instanced_arrays.' );

        position = geometry.attributes.position

        if position.my_class(isInterleavedBufferAttribute):
            count = position.data.count
            self.extensions.drawArraysInstancedANGLE( self.mode, 0, count, geometry.maxInstancedCount )
        else:
            self.extensions.drawArraysInstancedANGLE( self.mode, start, count, geometry.maxInstancedCount )

        self.infoRender.calls += 1
        self.infoRender.vertices += count * geometry.maxInstancedCount

        if self.mode == GL_TRIANGLES:
            self.infoRender.faces += geometry.maxInstancedCount * count / 3
        elif self.mode == GL_POINTS:
            self.infoRender.points += geometry.maxInstancedCount * count
