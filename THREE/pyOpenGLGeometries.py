"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from OpenGL_accelerate import *
from OpenGL.GL import *
from THREE.BufferGeometry import *
import THREE


class pyOpenGLGeometries:
    def __init__( self, attributes, infoMemory):
        self.geometries = {}
        self.wireframeAttributes = {}
        self.attributes = attributes
        self.infoMemory = infoMemory

    def onGeometryDispose(self, event):
        geometry = event.target
        buffergeometry = self.geometries[geometry.id]

        if buffergeometry.index:
            self.attributes.remove(buffergeometry.index)

        for name in buffergeometry.attributes:
            self.attributes.remove(buffergeometry.attributes[name])

        del self.geometries[geometry.id]

        # // TODO Remove duplicate code
        attribute = self.wireframeAttributes[geometry.id]

        if attribute:
            self.attributes.remove(attribute)
            del self.wireframeAttributes[geometry.id]

        attribute = self.wireframeAttributes[buffergeometry.id]

        if attribute:
            self.attributes.remove(attribute)
            del self.wireframeAttributes[buffergeometry.id]

        # //

        self.infoMemory.geometries -= 1

    def get(self, object, geometry):
        if geometry.id in self.geometries:
            buffergeometry = self.geometries[geometry.id]
            return buffergeometry

        geometry.onDispose(self.onGeometryDispose)

        if geometry.my_class(isBufferGeometry):
            buffergeometry = geometry
        elif geometry.my_class(isGeometry):
            if geometry._bufferGeometry is None:
                geometry._bufferGeometry = BufferGeometry().setFromObject(object)

            buffergeometry = geometry._bufferGeometry

        self.geometries[geometry.id] = buffergeometry

        self.infoMemory.geometries += 1

        return buffergeometry

    def update(self, geometry):
        updated = False
        index = geometry.index
        geometryAttributes = geometry.attributes
        if geometry.my_class(isInstancedBufferGeometry):
            maxInstancedCount = geometry.maxInstancedCount

        if index:
            data = self.attributes.update( index, GL_ELEMENT_ARRAY_BUFFER)
            if data.updated:
                updated = True

        for attribute in geometryAttributes.__dict__.values():
            if attribute is not None:
                if attribute.my_class(isInstancedBufferAttribute):
                    attribute.maxInstancedCount = maxInstancedCount
                data = self.attributes.update(attribute, GL_ARRAY_BUFFER)
                if data.updated and not updated:
                    updated = True

        # // morph targets
        for array in geometry.morphAttributes.__dict__.values():
            if not len(array):
                continue

            for morphAttribute in array:
                data = self.attributes.update(morphAttribute, GL_ARRAY_BUFFER)
                if data.updated and not updated:
                    updated = True

        return updated

    def getWireframeAttribute(self, geometry):
        if geometry.id in self.wireframeAttributes:
            return self.wireframeAttributes[geometry.id]

        indices = []

        geometryIndex = geometry.index
        geometryAttributes = geometry.attributes

        # // console.time( 'wireframe' );

        if geometryIndex:
            array = geometryIndex.array

            for i in range(0, len(array), 3):
                a = array[ i + 0 ]
                b = array[ i + 1 ]
                c = array[ i + 2 ]

                indices.extend([a, b, b, c, c, a])
        else:
            array = geometryAttributes.position.array

            for i in range(0, int(len(array) / 3) - 1, 3):
                a = i + 0
                b = i + 1
                c = i + 2

                indices.extend([a, b, b, c, c, a])

        # // console.timeEnd( 'wireframe' );
        if arrayMax(indices) > 65535:
            attribute = Uint32BufferAttribute(indices, 1)
        else:
            attribute = Uint16BufferAttribute( indices, 1)

        self.attributes.update(attribute, GL_ELEMENT_ARRAY_BUFFER)

        self.wireframeAttributes[geometry.id] = attribute

        return attribute
