"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from OpenGL_accelerate import *
from OpenGL.GL import *
from THREE.BufferGeometry import *
import THREE


class _pyOpenGLGeometryReference:
    def __init__(self, bufferGeometry, uuid):
        self.bufferGeometry = bufferGeometry
        self.objects = {uuid: True}


class pyOpenGLGeometries:
    def __init__( self, attributes, infoMemory):
        self.geometries = {}
        self.wireframeAttributes = {}
        self.attributes = attributes
        self.infoMemory = infoMemory

    def dispose(self, object, geometry):
        if object is None:
            return

        if geometry.id not in self.geometries:
            return

        reference = self.geometries[geometry.id]

        # decrease references
        if object.uuid in reference.objects:
            del reference.objects[object.uuid]

            if len(reference.objects) == 0:
                buffergeometry = reference.bufferGeometry
                if buffergeometry.index:
                    self.attributes.dispose(buffergeometry.index, buffergeometry)

                for name in buffergeometry.attributes.__dict__:
                    attribute = buffergeometry.attributes.__dict__[name]
                    if attribute:
                        self.attributes.dispose(attribute, buffergeometry)

                del self.geometries[geometry.id]

                if geometry.id in self.wireframeAttributes:
                    attribute = self.wireframeAttributes[geometry.id]
                    if attribute:
                        self.attributes.dispose(attribute, buffergeometry)
                        del self.wireframeAttributes[geometry.id]

                self.infoMemory.geometries -= 1

    def get(self, object, geometry):
        if geometry.id in self.geometries:
            geometry_reference = self.geometries[geometry.id]
            uuid = object.uuid
            if uuid not in geometry_reference.objects:
                geometry_reference.objects[uuid] = True

            buffergeometry = geometry_reference.bufferGeometry
            return buffergeometry

        if geometry.my_class(isBufferGeometry):
            buffergeometry = geometry
        elif geometry.my_class(isGeometry):
            if geometry._bufferGeometry is None:
                geometry._bufferGeometry = BufferGeometry().setFromObject(object)

            buffergeometry = geometry._bufferGeometry

        self.geometries[geometry.id] = _pyOpenGLGeometryReference(buffergeometry, object.uuid)

        self.infoMemory.geometries += 1

        return buffergeometry

    def update(self, geometry):
        updated = False
        index = geometry.index
        geometryAttributes = geometry.attributes
        if geometry.my_class(isInstancedBufferGeometry):
            maxInstancedCount = geometry.maxInstancedCount

        if index:
            data = self.attributes.update( index, GL_ELEMENT_ARRAY_BUFFER, geometry)
            if data.updated:
                updated = True

        for attribute in geometryAttributes.__dict__.values():
            if attribute is not None:
                if attribute.my_class(isInstancedBufferAttribute):
                    if maxInstancedCount is None:
                        maxInstancedCount = attribute.count * attribute.meshPerAttribute
                    attribute.maxInstancedCount = maxInstancedCount
                data = self.attributes.update(attribute, GL_ARRAY_BUFFER, geometry)
                if data.updated and not updated:
                    updated = True

        # // morph targets
        for array in geometry.morphAttributes.__dict__.values():
            if not len(array):
                continue

            for morphAttribute in array:
                data = self.attributes.update(morphAttribute, GL_ARRAY_BUFFER, geometry)
                if data.updated and not updated:
                    updated = True

        return updated

    def getWireframeAttribute(self, geometry):
        index = geometry.index
        if index is not None and index.uuid in self.wireframeAttributes:
            return self.wireframeAttributes[index.uuid]

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

        self.attributes.update(attribute, GL_ELEMENT_ARRAY_BUFFER, geometry)

        if index is not None:
            self.wireframeAttributes[index.uuid] = attribute
        else:
            self.wireframeAttributes[geometry.id] = attribute

        return attribute
