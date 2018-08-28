"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.BufferGeometry import *
from OpenGL_accelerate import *
from OpenGL.GL import *


class pyOpenGLObjects:
    def __init__(self, geometries, info):
        self.updateList = {}
        self.info = info
        self.geometries = geometries

    def update(self, object):
        frame = self.info.render.frame

        geometry = object.geometry
        buffergeometry = self.geometries.get(object, geometry)

        # // Update once per frame

        if buffergeometry.id not in self.updateList:
            self.updateList[buffergeometry.id] = -1

        if self.updateList[ buffergeometry.id ] != frame:
            if geometry.my_class(isGeometry):
                buffergeometry.updateFromObject(object)

            self.geometries.update(buffergeometry)

            self.updateList[buffergeometry.id] = frame

        return buffergeometry

    def dispose(self, object):
        geometry = object.geometry
        self.geometries.dispose(object, geometry)

    def clear(self):
        self.updateList.clear()