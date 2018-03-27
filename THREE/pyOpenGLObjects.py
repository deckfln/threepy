"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.BufferGeometry import *
from OpenGL_accelerate import *
from OpenGL.GL import *


class pyOpenGLObjects:
    def __init__(self, geometries, infoRender):
        self.updateList = {}
        self.infoRender = infoRender
        self.geometries = geometries

    def update(self, object):
        frame = self.infoRender.frame

        geometry = object.geometry
        buffergeometry = self.geometries.get(object, geometry)

        # // Update once per frame

        if buffergeometry.id not in self.updateList:
            self.updateList[buffergeometry.id] = -1

        if self.updateList[ buffergeometry.id ] != frame:
            if geometry.my_class(isGeometry):
                buffergeometry.updateFromObject(object)

            if object.vao == 0:
                object.vao = glGenVertexArrays(1)
                object.update_vao = True
                glBindVertexArray(object.vao)

                self.geometries.update(buffergeometry)

                glBindVertexArray(0)
                glBindBuffer(GL_ARRAY_BUFFER, 0)
            else:
                # object.update_vao = self.geometries.update(buffergeometry)
                self.geometries.update(buffergeometry)
                glBindBuffer(GL_ARRAY_BUFFER, 0)

            self.updateList[buffergeometry.id] = frame

        return buffergeometry

    def clear(self):
        self.updateList = {}
