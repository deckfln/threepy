"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author mikael emtinger / http:# //gomo.se/
 * @author alteredq / http:# //alteredqualia.com/
 * @author WestLangley / http:# //github.com/WestLangley
 * @author elephantatwork / www.elephantatwork.ch
 */
"""
import json

import THREE._Math as _Math
from THREE.math.Matrix3 import *
from THREE.math.Euler import *
from THREE.math.Quaternion import *
from THREE.core.Layers import *

_object3DId = 0

_matrix4 = Matrix4()
_vector3 = Vector3()


class Object3D(pyOpenGLObject):
    DefaultUp = Vector3(0, 1, 0)
    DefaultMatrixAutoUpdate = True
    isObject3D = True

    def __init__(self):
        global _object3DId
        self.id = _object3DId
        _object3DId += 1

        super().__init__()
        self.set_class(isObject3D)

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

        self._old_position = Vector3()
        self._old_quaternion = Quaternion()
        self._old_scale = Vector3()

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

        self._onBeforeRender = None
        self._onBeforeRenderParent = None

        self._onAfterRender = None
        self._onAfterRenderParent = None

        self.customDepthMaterial = None

        self.vao = [None, None, None]
        self.update_vao = [True, True, True]

    def __iter__(self):
        return iter(self.__dict__)

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def onBeforeRender(self, renderer, scene, camera, geometry, material=None, group=None):
        if self._onBeforeRender:
            return self._onBeforeRender(self, renderer, scene, camera)

        return True

    def setOnBeforeRender(self, object, func):
        self._onBeforeRender = func
        self._onBeforeRenderParent = object

    def onAfterRender(self, renderer, scene, camera, geometry=None, material=None, group=None):
        if self._onAfterRender:
            return self._onAfterRender(self, renderer, scene, camera)
        return True

    def setOnAfterRender(self, object, func):
        self._onAfterRender = func
        self._onAfterRenderParent = object

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
    quaternion = property(onQuaternionRead, onQuaternionChange)

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

    def rotateOnWorldAxis(self, axis, angle):
        """
        // rotate object on axis in world space
        // axis is assumed to be normalized
        // method assumes no rotated parent
        """
        q1 = Quaternion()

        q1.setFromAxisAngle( axis, angle )

        self.quaternion.premultiply( q1 )

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
        return vector.applyMatrix4(_matrix4.getInverse(self.matrixWorld))

    def lookAt(self, x, y=None, z=None):
        # // This method does not support objects with rotated and/or translated parent(s)
        if isinstance(x, float):
            _vector3.set(x, y, z)
        else:
            _vector3.copy(x)

        if self.my_class(isCamera):
            _matrix4.lookAt(self.position, _vector3, self.up)
        else:
            _matrix4.lookAt(_vector3, self.position, self.up)

        self._quaternion.setFromRotationMatrix(_matrix4)
            
    def add(self, object):
        if isinstance(object, list):
            for i in object:
                self.add(i)
            return self

        if object == self:
            raise RuntimeError("THREE.Object3D.add: object can't be added as a child of itself.", object)

        if object and object.isObject3D:
            if object.parent is not None:
                object.parent.remove(object)

            object.parent = self
            self.children.append(object)
        else:
            raise RuntimeError("THREE.Object3D.add: object not an instance of THREE.Object3D.", object)

        return self

    def remove(self, object):
        if isinstance(object, list):
            for i in object:
                self.remove(i)
            return self

        if object in self.children:
            index = self.children.index(object)
            object.parent = None
            del self.children[index]

        return self

    def getObjectByProperty(self, name, value):
        if self.name == value:
            return self

        for child in self.children:
            object = child.getObjectByProperty(name, value)

            if object is not None:
                return object

        return None

    def getObjectById(self, id):
        return self.getObjectByProperty('id', id)

    def getObjectByName(self, name):
        return self.getObjectByProperty('name', name)
        
    def getWorldPosition(self, target):
        self.updateMatrixWorld(True)

        return target.setFromMatrixPosition(self.matrixWorld)

    def getWorldQuaternion(self, target):
        position = Vector3()
        scale = Vector3()

        self.updateMatrixWorld(True)

        self.matrixWorld.decompose(position, target, scale)

        return target

    def getWorldScale(self, target):
        position = Vector3()
        quaternion = Quaternion()

        self.updateMatrixWorld(True)

        self.matrixWorld.decompose(position, quaternion, target)

        return target

    def getWorldDirection(self, target):
        quaternion = Quaternion()

        self.getWorldQuaternion(quaternion)

        return target.set(0, 0, 1).applyQuaternion(quaternion)

    def raycast(self, raycaster, intersects):
        return None

    def traverse(self, callback, scope=None):
        callback(self, scope)
        children = self.children
        for child in children:
            child.traverse(callback)

    def traverseVisible(self, callback):
        if not self.visible:
            return

        callback(self)

        children = self.children

        for child in children:
            child.traverseVisible(callback)

    def traverseAncestors(self, callback):
        parent = self.parent
        if parent is not None:
            callback(parent)
            parent.traverseAncestors(callback)

    def updateMatrix(self):
        if self._old_position.equals(self.position) and \
            self._old_quaternion.equals(self._quaternion) and \
            self._old_scale.equals(self.scale):
            self.matrix.updated = False
        else:
            self._old_position.copy(self.position)
            self._old_quaternion.copy(self._quaternion)
            self._old_scale.copy(self.scale)

            self.matrix.compose(self.position, self._quaternion, self.scale)
            self.matrix.updated = True

        self.matrixWorldNeedsUpdate = True

    def updateMatrixWorld(self, force=False):
        # bold optimization
        # do NOT compute the matrices for hidden objects
        if not self.visible:
            return

        if self.matrixAutoUpdate:
            self.updateMatrix()

        self.matrixWorld.updated = False
        if self.matrixWorldNeedsUpdate or force:
            if self.parent is None:
                self.matrixWorld.copy(self.matrix)
                self.matrixWorld.updated = True
            elif self.parent.matrixWorld.updated or self.matrix.updated:
                self.matrixWorld.multiplyMatrices(self.parent.matrixWorld, self.matrix)
                self.matrixWorld.updated = True

            self.matrixWorldNeedsUpdate = False

            force = True

        # // update children
        children = self.children
        for child in children:
            if child is not None:
                child.updateMatrixWorld(force)

    def toJSON(self, meta):
        # // meta is a string when called from JSON.stringify
        isRootObject = (meta is None or type(meta) is str)
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
                'images': {},
                'shapes': {}
            }

            output['metadata'] = {
                'version': '4.5',
                'type': 'Object',
                'generator': 'Object3D.toJSON'
            }

        # // standard Object3D serialization
        object = {}
        object['uuid'] = self.uuid
        object['type'] = self.type
        object['position'] = self.position.toArray()

        if self.name != '':
            object['name'] = self.name
        if self.castShadow:
            object['castShadow'] = True
        if self.receiveShadow:
            object['receiveShadow'] = True
        if not self.visible:
            object['visible'] = False
        if not self.frustumCulled:
            object['frustumCulled'] = False
        if self.renderOrder != 0:
            object['renderOrder'] = self.renderOrder

        if json.dumps(self.userData) != '{}':
            object['userData'] = self.userData

        object['layers'] = self.layers.mask
        object['matrix'] = self.matrix.toArray()
        if not self.matrixAutoUpdate:
            object['matrixAutoUpdate'] = False

        # //
        def serialize(library, element):
            if element.uuid  not in library:
                library[ element.uuid ] = element.toJSON(meta)

            return element.uuid

        if self.my_class(isMesh | isLine | isPoints):
            object['geometry'] = serialize(meta['geometries'], self.geometry)
            parameters = self.geometry.parameters

            if parameters is not None and parameters.shapes is not None:

                shapes = parameters.shapes

                if type( shapes ) is list:
                   for shape in shapes:
                        serialize( meta.shapes, shape )

                else:
                    serialize( meta.shapes, shapes )

        if self.material is not None:
            if isinstance(self.material, list):
                uuids = []
                for material in self.material:
                    uuids.append(serialize(meta['materials'], material))

                object['material'] = uuids
            else:
                object['material'] = serialize(meta['materials'], self.material)

        # //
        if len(self.children) > 0:
            object['children'] = []
            for i in range(len(self.children)):
                object['children'].append(self.children[ i].toJSON(meta).object)


        # // extract data from the cache hash
        # // remove metadata on each item
        # // and return as array
        def extractFromCache(cache):
            values = []
            for key in cache:
                data = cache[ key ]
                del data['metadata']
                values.append(data)

            return values
                
        if isRootObject:
            geometries = extractFromCache(meta['geometries'])
            materials = extractFromCache(meta['materials'])
            textures = extractFromCache(meta['textures'])
            images = extractFromCache(meta['images'])
            shapes = extractFromCache(meta['shapes'])

            if len(geometries) > 0:
                output['geometries'] = geometries
            if len(materials) > 0:
                output['materials'] = materials
            if len(textures) > 0:
                output['textures'] = textures
            if len(images) > 0:
                output['images'] = images
            if len(shapes) > 0:
                output['shapes'] = shapes

        output['object'] = object

        return output

    def clone(self, recursive=True):
        return type(self)().copy(self, recursive)

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

        self.userData = json.loads(json.dumps(source.userData))

        if recursive:
            for child in source.children:
                self.add(child.clone())

        return self

    def rebuild_id(self):
        global _object3DId
        self.id = _object3DId
        _object3DId += 1

        if self.geometry is not None:
            self.geometry.rebuild_id()
        if self.material is not None:
            if isinstance(self.material, list):
                for material in self.material:
                    material.rebuild_id()
            else:
                self.material.rebuild_id()

        for child in self.children:
            child.rebuild_id()

