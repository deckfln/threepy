"""
    /**
     * @author mrdoob / http://mrdoob.com/
     * @author kile / http://kile.stravaganza.org/
     * @author philogb / http://blog.thejit.org/
     * @author mikael emtinger / http://gomo.se/
     * @author egraether / http://egraether.com/
     * @author WestLangley / http://github.com/WestLangley
     */
"""

import THREE._Math as _Math
from THREE.pyOpenGLObject import *
from THREE.cython.cVector3 import *

_cython = False

_matrix4 = None


class Vector3(pyOpenGLObject):
    isVector3 = True

    def __init__(self, x=0, y=0, z=0):
        super().__init__()
        self.set_class(isVector3)
        self.np = np.array([x, y, z], np.float32)
        self.array = np.array([0, 0, 0, 1], np.float32)
        self.updated = False

    def is_updated(self):
        u = self.updated
        self.updated = False
        return u

    def set(self, x, y, z):
        vnp = self.np
        vnp[0] = x
        vnp[1] = y
        vnp[2] = z

        self.updated = True
        return self

    def setScalar(self, scalar):
        vnp = self.np
        vnp[0] = vnp[1] = vnp[2] = scalar
        self.updated = True
        return self

    def setX(self, x):
        self.np[0] = x
        self.updated = True
        return self

    def setY(self, y):
        self.np[1] = y
        self.updated = True
        return self

    def setZ(self, z):
        self.np[2] = z
        self.updated = True
        return self

    def getX(self):
        return self.np[0]

    def getY(self):
        return self.np[1]

    def getZ(self):
        return self.np[2]

    x = property(getX, setX)
    y = property(getY, setY)
    z = property(getZ, setZ)

    def setComponent(self, index, value):
        if index == 0:
            self.np[0] = value
        elif index == 1:
            self.np[1] = value
        elif index == 2:
            self.np[2] = value
        elif index == 'x':
            self.np[0] = value
        elif index == 'y':
            self.np[1] = value
        elif index == 'z':
            self.np[2] = value
        else:
            print('index is out of range: ' + index)

        self.updated = True
        return self

    def getComponent(self, index):
        if index == 0:
            return self.np[0]
        elif index == 1:
            return self.np[1]
        elif index == 2:
            return self.np[2]
        else:
            print('index is out of range: ' + index)

    def clone(self):
        return type(self)(self.np[0], self.np[1], self.np[2])

    def _copy(self, v):
        vnp = v.np
        snp = self.np
        snp[0] = vnp[0]
        snp[1] = vnp[1]
        snp[2] = vnp[2]

    def copy(self, v):
        global _cython
        if _cython:
            cVector3_copy(self, v)
        else:
            self._copy(v)
        self.updated = True
        return self

    def add(self, v, w=None):
        if w is not None:
            print('THREE.Vector3: .add() now only accepts one argument. Use .addVectors( a, b ) instead.')
            return self.addVectors(v, w)

        self.np += v.np

        self.updated = True
        return self

    def addScalar(self, s):
        self.np += s
        self.updated = True
        return self

    def addVectors(self, a, b):
        self.np = a.np + b.np
        self.updated = True
        return self

    def addScaledVector(self, v, s):
        self.np += v.np * s
        self.updated = True
        return self

    def sub(self, v, w=None):
        if w is not None:
            print('THREE.Vector3: .sub() now only accepts one argument. Use .subVectors( a, b ) instead.')
            return self.subVectors(v, w)

        self.np -= v.np
        self.updated = True
        return self

    def subScalar(self, s):
        self.np -= s
        self.updated = True
        return self

    def subVectors(self, a, b):
        self.np = a.np - b.np
        self.updated = True
        return self

    def multiply(self, v, w=None):
        if w is not None:
            print('THREE.Vector3: .multiply() now only accepts one argument. Use .multiplyVectors( a, b ) instead.')
            return self.multiplyVectors(v, w)

        self.np *= v.np
        self.updated = True
        return self

    def multiplyScalar(self, scalar):
        self.np *= scalar
        self.updated = True
        return self

    def multiplyVectors(self, a, b):
        self.np = a.np * b.np
        self.updated = True
        return self

    def applyEuler(self, euler):
        quaternion = Quaternion()
        if not( euler and euler.isEuler):
            print('THREE.Vector3: .applyEuler() now expects an Euler rotation rather than a Vector3 and order.')

        return self.applyQuaternion(quaternion.setFromEuler(euler))

    def applyAxisAngle(self, axis, angle):
        quaternion = Quaternion()
        return self.applyQuaternion(quaternion.setFromAxisAngle(axis, angle))

    def applyMatrix3(self, m):
        global _cython
        if _cython:
            cVector3_applyMatrix3(self, m)
        else:
            self._applyMatrix3(m)
        self.updated = True
        return self

    def _applyMatrix3(self, m):
        self.np.dot(m.matrix)

    def applyMatrix4(self, m):
        global _cython
        if _cython:
            cVector3_applyMatrix4(self, m)
        else:
            self._applyMatrix4(m)
        self.updated = True
        return self

    def _applyMatrix4(self, m):
        np.put(self.array, (0, 1, 2), self.np)
        c = np.dot(self.array, m.matrix)

        if c[3] == 0:
            self.z = float("-inf")
            return self

        c /= c[3]

        np.put(self.np, (0, 1, 2), c)

    def applyQuaternion(self, q):
        x = self.np[0]
        y = self.np[1]
        z = self.np[2]
        qx = q.x
        qy = q.y
        qz = q.z
        qw = q.w

        # # // calculate quat * vector

        ix = qw * x + qy * z - qz * y
        iy = qw * y + qz * x - qx * z
        iz = qw * z + qx * y - qy * x
        iw = - qx * x - qy * y - qz * z

        # # // calculate result * inverse quat

        self.np[0] = ix * qw + iw * - qx + iy * - qz - iz * - qy
        self.np[1] = iy * qw + iw * - qy + iz * - qx - ix * - qz
        self.np[2] = iz * qw + iw * - qz + ix * - qy - iy * - qx

        self.updated = True
        return self

    def project(self, camera):
        global _matrix4
        if _matrix4 is None:
            _matrix4 = Matrix4()

        _matrix4.multiplyMatrices(camera.projectionMatrix, _matrix4.getInverse(camera.matrixWorld))
        return self.applyMatrix4(_matrix4)

    def unproject(self, camera):
        global _matrix4
        if _matrix4 is None:
            _matrix4 = Matrix4()

        _matrix4.multiplyMatrices(camera.matrixWorld, _matrix4.getInverse(camera.projectionMatrix))
        return self.applyMatrix4(_matrix4)

    def transformDirection(self, m):
        # // input: THREE.Matrix4 affine matrix
        # // vector interpreted as a direction

        x = self.np[0]
        y = self.np[1]
        z = self.np[2]
        e = m.elements

        self.np[0] = e[0] * x + e[4] * y + e[8] * z
        self.np[1] = e[1] * x + e[5] * y + e[9] * z
        self.np[2] = e[2] * x + e[6] * y + e[10] * z

        return self.normalize()

    def divide(self, v):
        self.np /= v.np

        self.updated = True
        return self

    def divideScalar(self, scalar):
        return self.multiplyScalar(1 / scalar)

    def min(self, v):
        self.np = np.fmin(self.np, v.np)
        self.updated = True
        return self

    def max(self, v):
        self.np = np.fmax(self.np, v.np)
        self.updated = True
        return self

    def clamp(self, min, max):
        # // assumes min < max, componentwise
        self.np[0] = max(min.np[0], min(max.np[0], self.np[0]))
        self.np[1] = max(min.np[1], min(max.np[1], self.np[1]))
        self.np[2] = max(min.np[2], min(max.np[2], self.np[2]))

        self.updated = True
        return self

    def clampScalar(self, minVal, maxVal):
        min = Vector3()
        max = Vector3()

        min.set(minVal, minVal, minVal)
        max.set(maxVal, maxVal, maxVal)

        return self.clamp( min, max )

    def clampLength(self, min, max):
        length = self.length()
        return self.divideScalar(length or 1).multiplyScalar(max(min, min(max, length)))

    def floor(self):
        self.np = np.floor(self.np)
        self.updated = True
        return self

    def ceil(self):
        self.np = np.ceil(self.np)
        self.updated = True
        return self

    def round(self):
        self.np = np.round(self.np)
        self.updated = True
        return self

    def roundToZero(self):
        self.np[0] = math.floor(self.np[0])
        if self.np[0] < 0:
            self.np[0] = math.ceil(self.np[0])
        self.np[1] = math.floor(self.np[1])
        if self.np[1] < 0:
            self.np[1] = math.ceil(self.np[1])
        self.np[2] = math.floor(self.np[2])
        if self.np[2] < 0:
            self.np[2] = math.ceil(self.np[2])

        self.updated = True
        return self

    def negate(self):
        self.np = -self.np

        self.updated = True
        return self

    def dot(self, v):
        self.updated = True
        return self.np.dot(v.np)

    # // TODO lengthSquared?
    def lengthSq(self):
        s1 = np.dot(self.np, self.np)
        return s1

    def length(self):
        return math.sqrt(self.lengthSq())

    def manhattanLength(self):
        return abs(self.np[0]) + abs(self.np[1]) + abs(self.np[2])

    def normalize(self):
        return self.divideScalar(self.length() or 1)

    def setLength(self, length):
        return self.normalize().multiplyScalar(length)

    def lerp(self, v, alpha):
        global _cython
        if _cython:
            cVector3_lerp(self.np, v.np, alpha)
        else:
            self._plerp(v, alpha)
        self.updated = True
        return self

    def _plerp(self, v, alpha):
        """
        self.np[0] += ( v.np[0] - self.np[0] ) * alpha
        self.np[1] += ( v.np[1] - self.np[1] ) * alpha
        self.np[2] += ( v.np[2] - self.np[2] ) * alpha
        """
        self.np += (v.np - self.np) * alpha

        return self

    def lerpVectors(self, v1, v2, alpha):
        return self.subVectors(v2, v1).multiplyScalar(alpha).add(v1)

    def cross(self, v, w=None):
        if w is not None:
            print('THREE.Vector3: .cross() now only accepts one argument. Use .crossVectors( a, b ) instead.')
            return self.crossVectors(v, w)

        self.np = np.cross(self.np, v.np)

        self.updated = True
        return self

    def crossVectors(self, a, b):
        self.np = np.cross(a.np, b.np)

        self.updated = True
        return self

    def projectOnVector(self, vector):
        scalar = vector.dot(self) / vector.lengthSq()

        return self.copy(vector).multiplyScalar(scalar)

    def projectOnPlane(self, planeNormal):
        v1 = Vector3()
        v1.copy(self).projectOnVector(planeNormal)
        return self.sub(v1)

    def reflect(self, normal):
        # // reflect incident vector off plane orthogonal to normal
        # // normal is assumed to have unit length
        v1 = Vector3()
        return self.sub(v1.copy(normal).multiplyScalar(2 * self.dot(normal)))

    def angleTo(self, v):
        theta = self.dot(v) / (math.sqrt( self.lengthSq() * v.lengthSq()))

        # // clamp, to handle numerical problems

        return math.acos(_Math.clamp(theta, - 1, 1))

    def distanceTo(self, v):
        return math.sqrt(self.distanceToSquared(v))

    def distanceToSquared(self, v):
        dm = np.subtract(self.np, v.np)
        d = np.dot(dm, dm)
        return d

    def manhattanDistanceTo(self, v):
        return abs(self.np[0] - v.np[0]) + abs(self.np[1] - v.np[1]) + abs(self.np[2] - v.np[2])

    def setFromSpherical(self, s):
        sinPhiRadius = math.sin(s.phi) * s.radius
        self.np[0] = sinPhiRadius * math.sin(s.theta)
        self.np[1] = math.cos(s.phi) * s.radius
        self.np[2] = sinPhiRadius * math.cos(s.theta)
        self.updated = True
        return self

    def setFromCylindrical(self, c ):
        self.np[0] = c.radius * math.sin(c.theta)
        self.np[1] = c.y
        self.np[2] = c.radius * math.cos(c.theta)

        self.updated = True
        return self

    def setFromMatrixPosition(self, m):
        self.np[0:3] = m.elements[12:15]
        self.updated = True
        return self

    def setFromMatrixScale(self, m):
        sx = self.setFromMatrixColumn(m, 0).length()
        sy = self.setFromMatrixColumn(m, 1).length()
        sz = self.setFromMatrixColumn(m, 2).length()

        self.np[0] = sx
        self.np[1] = sy
        self.np[2] = sz

        self.updated = True
        return self

    def setFromMatrixColumn(self, m, index):
        return self.fromArray(m.elements, index * 4)

    def _equals(self, v):
        vnp = v.np
        snp = self.np
        return vnp[0] == snp[0] and vnp[1] == snp[1] and vnp[2] == snp[2]

    def equals(self, v):
        global _cython
        if _cython:
            return cVector_equals(self, v)

        return self._equals(v)

    def less_than(self, v):
        global _cython
        if _cython:
            return cVector3_less_than(self.np, v.np)

        return np.any(self.np < v.np)

    def greater_than(self, v):
        global _cython
        if _cython:
            return cVector3_greater_than(self.np, v.np)

        return np.any(self.np > v.np)

    def fromArray(self, array, offset=0):
        self.np[0:3] = array[offset:offset+3]
        self.updated = True
        return self

    def toArray(self, array=None, offset=0):
        if array is None:
            array = [0, 0, 0]

        array[offset:offset+3] = self.np[0:3]

        return array

    def fromBufferAttribute(self, attribute, index, offset=None):
        if offset is not None:
            print('THREE.Vector3: offset has been removed from .fromBufferAttribute().')

        self.np[0] = attribute.getX(index)
        self.np[1] = attribute.getY(index)
        self.np[2] = attribute.getZ(index)

        self.updated = True
        return self


from THREE.math.Matrix4 import *
from THREE.math.Quaternion import *
