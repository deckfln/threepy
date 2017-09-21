"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.BufferGeometry import *


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
            if hasattr(geometry, 'isGeometry'):
                buffergeometry.updateFromObject(object)

            self.geometries.update(buffergeometry)

            self.updateList[buffergeometry.id] = frame

        return buffergeometry

    def clear(self):
        self.updateList = {}
