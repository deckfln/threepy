"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author mikael emtinger / http:# //gomo.se/
 * @author alteredq / http:# //alteredqualia.com/
 * @author WestLangley / http:# //github.com/WestLangley
 * @author elephantatwork / www.elephantatwork.ch
 */
"""
import THREE._Math as _Math
from THREE.RootObject import *
from THREE.Vector3 import *
from THREE.Matrix3 import *
from THREE.Matrix4 import *
from THREE.Euler import *
from THREE.Quaternion import *
from THREE.Layers import *


_object3DId = 0


class Object3D():
    DefaultUp = Vector3(0, 1, 0)
    DefaultMatrixAutoUpdate = True
    isObject3D = True

    def __init__(self):
        global _object3DId
        self.id = _object3DId
        _object3DId += 1

        self.uuid = _Math.generateUUID()

        self.name = ''
        self.type = 'Object3D'

        self.parent = None
        self.children = []

        self.up = Object3D.DefaultUp.clone()

        self.position = Vector3()
        self._rotation = Euler()
        self._rotation.onChange(self.onRotationChange)
        self._quaternion = Quaternion()
        self._quaternion.onChange(self.onQuaternionChange)
        self.scale = Vector3(1, 1, 1)
        self.modelViewMatrix = Matrix4()
        self.normalMatrix = Matrix3()
        self.matrix = Matrix4()
        self.matrixWorld = Matrix4()

        self.matrixAutoUpdate = Object3D.DefaultMatrixAutoUpdate
        self.matrixWorldNeedsUpdate = False

        self.layers = Layers()
        self.visible = True

        self.castShadow = False
        self.receiveShadow = False

        self.frustumCulled = True
        self.renderOrder = 0

        self.geometry = None
        self.material = None

        self.userData = {}
        
    def onRotationChange(self, rotation):
        self._rotation = rotation
        self._quaternion.setFromEuler(rotation, False)

    def onQuaternionChange(self, quaternion):
        self._quaternion = quaternion
        self._rotation.setFromQuaternion(quaternion, None, False)

    def onRotationRead(self):
        return self._rotation

    def onQuaternionRead(self):
        return self._quaternion

    rotation = property(onRotationRead, onRotationChange)
    quaternion = property(onRotationRead, onQuaternionChange)

    def applyMatrix(self, matrix):
        self.matrix.multiplyMatrices(matrix, self.matrix)
        self.matrix.decompose(self.position, self._quaternion, self.scale)

    def applyQuaternion(self, q):
        self._quaternion.premultiply(q)

        return self

    def setRotationFromAxisAngle(self, axis, angle):
        # // assumes axis is normalized
        self._quaternion.setFromAxisAngle(axis, angle)

    def setRotationFromEuler(self, euler):
        self._quaternion.setFromEuler(euler, True)

    def setRotationFromMatrix(self, m):
        # // assumes the upper 3x3 of m is a pure rotation matrix (i.e, unscaled)
        self._quaternion.setFromRotationMatrix(m)

    def setRotationFromQuaternion(self, q):
        # // assumes q is normalized
        self._quaternion.copy(q)

    def rotateOnAxis(self, axis, angle):
        # // rotate object on axis in object space
        # // axis is assumed to be normalized
        q1 = Quaternion().setFromAxisAngle(axis, angle)
        self._quaternion.multiply(q1)
        return self

    def rotateX(self, angle):
        v1 = Vector3(1, 0, 0)
        return self.rotateOnAxis(v1, angle)

    def rotateY(self, angle):
        v1 = Vector3(0, 1, 0)
        return self.rotateOnAxis(v1, angle)

    def rotateZ(self, angle):
        v1 = Vector3(0, 0, 1)
        return self.rotateOnAxis(v1, angle)

    def translateOnAxis(self, axis, distance):
        # // translate object by distance along axis in object space
        # // axis is assumed to be normalized
        v1 = Vector3().copy(axis).applyQuaternion(self._quaternion)
        self.position.add(v1.multiplyScalar(distance))
        return self

    def translateX(self, distance):
        v1 = Vector3(1, 0, 0)
        return self.translateOnAxis(v1, distance)

    def translateY(self, distance):
        v1 = Vector3(0, 1, 0)
        return self.translateOnAxis(v1, distance)

    def translateZ(self, distance):
        v1 = Vector3(0, 0, 1)
        return self.translateOnAxis(v1, distance)

    def localToWorld(self, vector):
        return vector.applyMatrix4(self.matrixWorld)

    def worldToLocal(self, vector):
        m1 = Matrix4()
        return vector.applyMatrix4(m1.getInverse(self.matrixWorld))

    def lookAt(self, x, y, z):
        # // This method does not support objects with rotated and/or translated parent(s)
        m1 = Matrix4()
        vector = Vector3()
        if x.isVector3:
            vector.copy(x)
        else:
            vector.set(x, y, z)

        if self.isCamera:
            m1.lookAt(self.position, vector, self.up)
        else:
            m1.lookAt(vector, self.position, self.up)

        self._quaternion.setFromRotationMatrix(m1)
            
    def add(self, object):
        if type(object) == list:
            for i in object:
                self.add(i)
            return self

        if object == self:
            raise("THREE.Object3D.add: object can't be added as a child of itself.", object)

        if object and object.isObject3D:
            if object.parent is not None :
                object.parent.remove(object)

            object.parent = self
            self.children.append(object)
        else:
            raise("THREE.Object3D.add: object not an instance of THREE.Object3D.", object)

        return self

    def remove(self, object):
        if type(object)==list:
            for i in object:
                self.remove(i)
            return self

        index = self.children.index(object)

        if index != - 1:
            object.parent = None
            del self.children[index]

        return self

    def getObjectByProperty(self, name, value):
        if self.name == value:
            return self

        for i in range(len(self.children)):
            child = self.children[ i ]
            object = child.getObjectByProperty(name, value)

            if object is not None:
                return object

        return None

    def getObjectById(self, id):
        return self.getObjectByProperty('id', id)

    def getObjectByName(self, name):
        return self.getObjectByProperty('name', name)
        
    def getWorldPosition(self, optionalTarget=None):
        result = optionalTarget or Vector3()

        self.updateMatrixWorld(True)

        return result.setFromMatrixPosition(self.matrixWorld)

    def getWorldQuaternion(self, optionalTarget=None):
        position = Vector3()
        scale = Vector3()

        result = optionalTarget or Quaternion()

        self.updateMatrixWorld(True)

        self.matrixWorld.decompose(position, result, scale)

        return result

    def getWorldRotation(self, optionalTarget=None):
        quaternion = Quaternion()

        result = optionalTarget or Euler()

        self.getWorldQuaternion(quaternion)

        return result.setFromQuaternion(quaternion, self._rotation.order, False)

    def getWorldScale(self, optionalTarget=None):
        position = Vector3()
        quaternion = Quaternion()

        result = optionalTarget or Vector3()

        self.updateMatrixWorld(True)

        self.matrixWorld.decompose(position, quaternion, result)

        return result

    def getWorldDirection(self, optionalTarget=None):
        quaternion = Quaternion()

        result = optionalTarget or Vector3()

        self.getWorldQuaternion(quaternion)

        return result.set(0, 0, 1).applyQuaternion(quaternion)

    def raycast(self):
        return None

    def traverse(self, callback):
        callback(self)
        children = self.children
        for i in range(len(children)):
            children[ i ].traverse(callback)

    def traverseVisible(self, callback):
        if not self.visible:
            return

        callback(self)

        children = self.children

        for i in range(len(children)):
            children[ i ].traverseVisible(callback)

    def traverseAncestors(self, callback):
        parent = self.parent
        if parent is not None:
            callback(parent)
            parent.traverseAncestors(callback)

    def updateMatrix(self):
        self.matrix.compose(self.position, self._quaternion, self.scale)

        self.matrixWorldNeedsUpdate = True

    def updateMatrixWorld(self, force=False):
        if self.matrixAutoUpdate:
            self.updateMatrix()

        if self.matrixWorldNeedsUpdate or force:
            if self.parent is None:
                self.matrixWorld.copy(self.matrix)
            else:
                self.matrixWorld.multiplyMatrices(self.parent.matrixWorld, self.matrix)

            self.matrixWorldNeedsUpdate = False

            force = True

        # // update children
        children = self.children
        for i in range(len(children)):
            children[ i ].updateMatrixWorld(force)

    def toJSON(self, meta):
        # // meta is '' when called from JSON.stringify
        isRootObject = (meta is None or meta == '')
        output = {}

        # // meta is a hash used to collect geometries, materials.
        # // not providing it implies that self is the root object
        # // being serialized.
        if isRootObject:
            # // initialize meta obj
            meta = {
                'geometries': {},
                'materials': {},
                'textures': {},
                'images': {}
            }

            output.metadata = {
                'version': '4.5',
                'type': 'Object',
                'generator': 'Object3D.toJSON'
            }

        # // standard Object3D serialization
        object = {}
        object.uuid = self.uuid
        object.type = self.type

        if self.name != '':
            object.name = self.name
        if self.castShadow:
            object.castShadow = True
        if self.receiveShadow:
            object.receiveShadow = True
        if not self.visible:
            object.visible = False
        if JSON.stringify(self.userData) != '{}':
            object.userData = self.userData

        object.matrix = self.matrix.toArray()

        # //
        def serialize(library, element):
            if library[ element.uuid ] is None:
                library[ element.uuid ] = element.toJSON(meta)

            return element.uuid

        if self.geometry is not None:
            object.geometry = serialize(meta.geometries, self.geometry)

        if self.material is not None:
            if type(self.material) == "array":
                uuids = []
                for i in range(len(self.material)):
                    uuids.append(serialize(meta.materials, self.material[ i ]))

                object.material = uuids
            else:
                object.material = serialize(meta.materials, self.material)

        # //
        if len(self.children) > 0:
            object.children = []
            for i in range(len(self.children)):
                object.children.append(self.children[ i ].toJSON(meta).object)


        # // extract data from the cache hash
        # // remove metadata on each item
        # // and return as array
        def extractFromCache(cache):
            values = []
            for key in cache:
                data = cache[ key ]
                del data.metadata
                values.push(data)

            return values
                
        if isRootObject:
            geometries = extractFromCache(meta.geometries)
            materials = extractFromCache(meta.materials)
            textures = extractFromCache(meta.textures)
            images = extractFromCache(meta.images)

            if len(geometries) > 0:
                output.geometries = geometries
            if len(materials) > 0:
                output.materials = materials
            if len(textures) > 0:
                output.textures = textures
            if len(images) > 0:
                output.images = images

        output.object = object

        return output

    def clone(self, recursive=True):
        return Object3D().copy(self, recursive)

    def copy(self, source, recursive=True):
        self.name = source.name

        self.up.copy(source.up)

        self.position.copy(source.position)
        self._quaternion.copy(source.quaternion)
        self.scale.copy(source.scale)

        self.matrix.copy(source.matrix)
        self.matrixWorld.copy(source.matrixWorld)

        self.matrixAutoUpdate = source.matrixAutoUpdate
        self.matrixWorldNeedsUpdate = source.matrixWorldNeedsUpdate

        self.layers.mask = source.layers.mask
        self.visible = source.visible

        self.castShadow = source.castShadow
        self.receiveShadow = source.receiveShadow

        self.frustumCulled = source.frustumCulled
        self.renderOrder = source.renderOrder

        self.userData = JSON.parse(JSON.stringify(source.userData))

        if recursive:
            for i in range(len(source.children)):
                child = source.children[ i ]
                self.add(child.clone())

        return self