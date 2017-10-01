"""
    /**
     * @author mrdoob / http://mrdoob.com/
     * @author WestLangley / http://github.com/WestLangley
     * @author bhouston / http://clara.io
     */
"""
import math
import THREE._Math as _Math
from THREE.Matrix4 import *
from THREE.Quaternion import *
from THREE.pyOpenGLObject import *
from numba import *


class Euler(pyOpenGLObject):
    RotationOrders = [ 'XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX' ]
    DefaultOrder = 'XYZ'
    isEuler = True
    
    def __init__(self, x=0, y=0, z=0, order='XYZ'):
        self._x = x
        self._y = y
        self._z = z
        self._order = order or Euler.DefaultOrder
        self.onChangeCallback = None
        
    def setX(self, x):
        self._x = x
        if self.onChangeCallback:
            self.onChangeCallback(self)

    def setY(self, y):
        self._y = y
        if self.onChangeCallback:
            self.onChangeCallback(self)

    def setZ(self, z):
        self._z = z
        if self.onChangeCallback:
            self.onChangeCallback(self)

    def setOrder(self, order):
        self._order = order
        if self.onChangeCallback:
            self.onChangeCallback(self)

    def getX(self):
        return self._x

    def getY(self):
        return self._y

    def getZ(self):
        return self._z

    def getOrder(self):
        return self._order

    x = property(getX, setX)
    y = property(getY, setY)
    z = property(getZ, setZ)
    order = property(getOrder, setOrder)

    def set(self, x, y, z, order):
        self._x = x
        self._y = y
        self._z = z
        self._order = order or self._order
        
        if self.onChangeCallback:
            self.onChangeCallback(self)

        return self

    def clone(self):
        return type(self)(self._x, self._y, self._z, self._order)

    def copy(self, euler):
        self._x = euler._x
        self._y = euler._y
        self._z = euler._z
        self._order = euler._order
        
        if self.onChangeCallback:
            self.onChangeCallback(self)

        return self

    @jit(cache=True)
    def setFromRotationMatrix(self, m, order=None, update=True):
        clamp = _Math.clamp

        # // assumes the upper 3x3 of m is a pure rotation matrix (i.e, unscaled)

        te = m.elements
        m11 = te[ 0 ]; m12 = te[ 4 ]; m13 = te[ 8 ]
        m21 = te[ 1 ]; m22 = te[ 5 ]; m23 = te[ 9 ]
        m31 = te[ 2 ]; m32 = te[ 6 ]; m33 = te[ 10 ]

        order = order or self._order

        if order == 'XYZ':
            self._y = math.asin(clamp(m13, - 1, 1))
            if abs(m13) < 0.99999:
                self._x = math.atan2(- m23, m33)
                self._z = math.atan2(- m12, m11)
            else:
                self._x = math.atan2(m32, m22)
                self._z = 0
        elif order == 'YXZ':
            self._x = math.asin(- clamp(m23, - 1, 1))
            if abs(m23) < 0.99999:
                self._y = math.atan2(m13, m33)
                self._z = math.atan2(m21, m22)
            else:
                self._y = math.atan2(- m31, m11)
                self._z = 0
        elif order == 'ZXY':
            self._x = math.asin(clamp(m32, - 1, 1))
            if abs(m32) < 0.99999:
                self._y = math.atan2(- m31, m33)
                self._z = math.atan2(- m12, m22)
            else:
                self._y = 0
                self._z = math.atan2(m21, m11)
        elif order == 'ZYX':
            self._y = math.asin(- clamp(m31, - 1, 1))
            if abs(m31) < 0.99999:
                self._x = math.atan2(m32, m33)
                self._z = math.atan2(m21, m11)
            else:
                self._x = 0
                self._z = math.atan2(- m12, m22)
        elif order == 'YZX':
            self._z = math.asin(clamp(m21, - 1, 1))
            if abs(m21) < 0.99999:
                self._x = math.atan2(- m23, m22)
                self._y = math.atan2(- m31, m11)
            else:
                self._x = 0
                self._y = math.atan2(m13, m33)
        elif order == 'XZY':
            self._z = math.asin(- clamp(m12, - 1, 1))
            if abs(m12) < 0.99999:
                self._x = math.atan2(m32, m22)
                self._y = math.atan2(m13, m11)
            else:
                self._x = math.atan2(- m23, m33)
                self._y = 0
        else:
            print('THREE.Euler: .setFromRotationMatrix() given unsupported order: ' + order)

        self._order = order
        if update and self.onChangeCallback:
            self.onChangeCallback(self)

        return self

    def setFromQuaternion(self, q, order, update=True):
        matrix = Matrix4().makeRotationFromQuaternion(q)
        return self.setFromRotationMatrix(matrix, order, update)

    def setFromVector3(self, v, order):
        return self.set(v.x, v.y, v.z, order or self._order)

    def reorder(self, newOrder):
        # // WARNING: self discards revolution information -bhouston
        q = Quaternion()
        q.setFromEuler(self)
        return self.setFromQuaternion(q, newOrder)

    def equals(self, euler):
        return (euler._x == self._x) and (euler._y == self._y) and (euler._z == self._z) and (euler._order == self._order)

    @jit(cache=True)
    def fromArray(self, array):
        self._x = array[ 0 ]
        self._y = array[ 1 ]
        self._z = array[ 2 ]
        if array[ 3 ] is not None:
            self._order = array[ 3 ]

        if self.onChangeCallback:
            self.onChangeCallback(self)
            
        return self

    @jit(cache=True)
    def toArray(self, array=None, offset=0):
        if array is None:
            array = []

        array[ offset ] = self._x
        array[ offset + 1 ] = self._y
        array[ offset + 2 ] = self._z
        array[ offset + 3 ] = self._order

        return array

    def toVector3(self, optionalResult=None):
        if optionalResult:
            return optionalResult.set(self._x, self._y, self._z)
        else:
            return Vector3(self._x, self._y, self._z)
            
    def onChange(self, callback):
        self.onChangeCallback = callback
        return self
