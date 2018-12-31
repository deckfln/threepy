"""
    /**
     * @author mikael emtinger / http://gomo.se/
     * @author alteredq / http://alteredqualia.com/
     * @author WestLangley / http://github.com/WestLangley
     * @author bhouston / http://clara.io
     */
"""

from THREE.math.Vector3 import *
from THREE.Constants import *
from THREE.cython.cthree import *
import numpy as np

from THREE.cython.cQuaternion import cQuaternion_setFromRotationMatrix, cQuaternion_multiplyQuaternions, cQuaternion_slerpFlat

_cython = True
_v1 = Vector3()
_temp = np.zeros(4, np.float32)


class Quaternion:
    def __init__(self, x=0, y=0, z=0, w=1):
        self.np = np.array([x, y, z, w], np.float32)
        self.onChangeCallback = None
        self.updated = True

    def is_updated(self):
        """
        Check if the matrix got updated and set the flag
        :return:
        """
        u = self.updated
        self.updated = False
        return u

    def setX(self, x):
        self.np[0] = x
        self.updated = True
        if self.onChangeCallback:
            self.onChangeCallback(self)

    def setY(self, y):
        self.np[1] = y
        self.updated = True
        if self.onChangeCallback:
            self.onChangeCallback(self)

    def setZ(self, z):
        self.np[2] = z
        self.updated = True
        if self.onChangeCallback:
            self.onChangeCallback(self)

    def setW(self, w):
        self.np[3] = w
        self.updated = True
        if self.onChangeCallback:
            self.onChangeCallback(self)

    def getX(self):
        return self.np[0]

    def getY(self):
        return self.np[1]

    def getZ(self):
        return self.np[2]

    def getW(self):
        return self.np[3]

    x = property(getX, setX)
    y = property(getY, setY)
    z = property(getZ, setZ)
    w = property(getW, setW)
        
    def slerp(self, qa, qb, qm=None, t=None):
        if qm is None:
            return self._slerp(qa, qb)
        else:
            return qm.copy(qa).slerp(qb, t)

    def slerpFlat(self, dst, dstOffset, src0, srcOffset0, src1, srcOffset1, t):
        if _cython:
            cQuaternion_slerpFlat(dst, dstOffset, src0, srcOffset0, src1, srcOffset1, t)
        else:
            self._slerpFlat(dst, dstOffset, src0, srcOffset0, src1, srcOffset1, t)

    def _slerpFlat(self, dst, dstOffset, src0, srcOffset0, src1, srcOffset1, t):
        # // fuzz-free, array-based Quaternion SLERP operation

        x0 = src0[srcOffset0 + 0]
        y0 = src0[srcOffset0 + 1]
        z0 = src0[srcOffset0 + 2]
        w0 = src0[srcOffset0 + 3]

        x1 = src1[srcOffset1 + 0]
        y1 = src1[srcOffset1 + 1]
        z1 = src1[srcOffset1 + 2]
        w1 = src1[srcOffset1 + 3]

        if w0 != w1 or x0 != x1 or y0 != y1 or z0 != z1:
            s = 1 - t
            cos = x0 * x1 + y0 * y1 + z0 * z1 + w0 * w1
            dir = -1
            if cos >= 0:
                dir = 1
            sqrSin = 1 - cos * cos

            # // Skip the Slerp for tiny steps to avoid numeric problems:
            if sqrSin > Number.EPSILON:
                sin = math.sqrt(sqrSin)
                len = math.atan2(sin, cos * dir)

                s = math.sin(s * len) / sin
                t = math.sin(t * len) / sin

            tDir = t * dir

            x0 = x0 * s + x1 * tDir
            y0 = y0 * s + y1 * tDir
            z0 = z0 * s + z1 * tDir
            w0 = w0 * s + w1 * tDir

            # // Normalize in case we just did a lerp:
            if s == 1 - t:
                f = 1 / math.sqrt(x0 * x0 + y0 * y0 + z0 * z0 + w0 * w0)
                
                x0 *= f
                y0 *= f
                z0 *= f
                w0 *= f

        dst[dstOffset] = x0
        dst[dstOffset + 1] = y0
        dst[dstOffset + 2] = z0
        dst[dstOffset + 3] = w0

    def set(self, x, y, z, w):
        self.np[0] = x
        self.np[1] = y
        self.np[2] = z
        self.np[3] = w

        if self.onChangeCallback:
            self.onChangeCallback(self)

        self.updated = True
        return self

    def clone(self):
        return type(self)(self.np[0], self.np[1], self.np[2], self.np[3])

    def copy(self, quaternion):
        self.np[:] = quaternion.np[:]

        if self.onChangeCallback:
            self.onChangeCallback(self)
        
        self.updated = True
        return self

    def setFromEuler(self, euler, update=False):
        if not (euler and euler.isEuler):
            print('THREE.Quaternion: .setFromEuler() now expects an Euler rotation rather than a Vector3 and order.')

        x = euler._x
        y = euler._y
        z = euler._z
        order = euler.order

        # // http://www.mathworks.com/matlabcentral/fileexchange/
        # //     20696-function-to-convert-between-dcm-euler-angles-quaternions-and-euler-vectors/
        # //    content/SpinCalc.m

        cos = math.cos
        sin = math.sin

        c1 = cos(x / 2)
        c2 = cos(y / 2)
        c3 = cos(z / 2)

        s1 = sin(x / 2)
        s2 = sin(y / 2)
        s3 = sin(z / 2)

        if order == 'XYZ':
            self.np[0] = s1 * c2 * c3 + c1 * s2 * s3
            self.np[1] = c1 * s2 * c3 - s1 * c2 * s3
            self.np[2] = c1 * c2 * s3 + s1 * s2 * c3
            self.np[3] = c1 * c2 * c3 - s1 * s2 * s3
        elif order == 'YXZ':
            self.np[0] = s1 * c2 * c3 + c1 * s2 * s3
            self.np[1] = c1 * s2 * c3 - s1 * c2 * s3
            self.np[2] = c1 * c2 * s3 - s1 * s2 * c3
            self.np[3] = c1 * c2 * c3 + s1 * s2 * s3
        elif order == 'ZXY':
            self.np[0] = s1 * c2 * c3 - c1 * s2 * s3
            self.np[1] = c1 * s2 * c3 + s1 * c2 * s3
            self.np[2] = c1 * c2 * s3 + s1 * s2 * c3
            self.np[3] = c1 * c2 * c3 - s1 * s2 * s3
        elif order == 'ZYX':
            self.np[0] = s1 * c2 * c3 - c1 * s2 * s3
            self.np[1] = c1 * s2 * c3 + s1 * c2 * s3
            self.np[2] = c1 * c2 * s3 - s1 * s2 * c3
            self.np[3] = c1 * c2 * c3 + s1 * s2 * s3
        elif order == 'YZX':
            self.np[0] = s1 * c2 * c3 + c1 * s2 * s3
            self.np[1] = c1 * s2 * c3 + s1 * c2 * s3
            self.np[2] = c1 * c2 * s3 - s1 * s2 * c3
            self.np[3] = c1 * c2 * c3 - s1 * s2 * s3
        elif order == 'XZY':
            self.np[0] = s1 * c2 * c3 - c1 * s2 * s3
            self.np[1] = c1 * s2 * c3 - s1 * c2 * s3
            self.np[2] = c1 * c2 * s3 + s1 * s2 * c3
            self.np[3] = c1 * c2 * c3 + s1 * s2 * s3

        if update:
            self.onChangeCallback(self)

        self.updated = True
        return self

    def setFromAxisAngle(self, axis, angle):
        # // http://www.euclideanspace.com/maths/geometry/rotations/conversions/angleToQuaternion/index.htm
        # // assumes axis is normalized
        global _temp

        halfAngle = angle / 2
        s = math.sin(halfAngle)

        _temp[0] = s
        _temp[1] = s
        _temp[2] = s
        _temp[3] = 1

        self.np[0] = axis.x
        self.np[1] = axis.y
        self.np[2] = axis.z
        self.np[3] = math.cos(halfAngle)
        self.np *= _temp

        if self.onChangeCallback:
            self.onChangeCallback(self)

        self.updated = True
        return self

    def setFromRotationMatrix(self, m):
        global _cython
        if _cython:
            cQuaternion_setFromRotationMatrix(self, m)
        else:
            self._setFromRotationMatrix(m)

        if self.onChangeCallback:
            self.onChangeCallback(self)

        self.updated = True
        return self

    def _setFromRotationMatrix(self, m):
        # // http://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToQuaternion/index.htm
        # // assumes the upper 3x3 of m is a pure rotation matrix (i.e, unscaled)
        global _temp

        te = m.elements
        m11 = te[0]; m12 = te[4]; m13 = te[8]
        m21 = te[1]; m22 = te[5]; m23 = te[9]
        m31 = te[2]; m32 = te[6]; m33 = te[10]

        trace = m11 + m22 + m33

        if trace > 0:
            s = 0.5 / math.sqrt(trace + 1.0)

            self.np[3] = 0.25 / s
            self.np[0] = (m32 - m23) * s
            self.np[1] = (m13 - m31) * s
            self.np[2] = (m21 - m12) * s
        elif m11 > m22 and m11 > m33:
            s = 2.0 * math.sqrt(1.0 + m11 - m22 - m33)

            self.np[3] = (m32 - m23) / s
            self.np[0] = 0.25 * s
            self.np[1] = (m12 + m21) / s
            self.np[2] = (m13 + m31) / s

        elif m22 > m33:
            s = 2.0 * math.sqrt(1.0 + m22 - m11 - m33)

            self.np[3] = (m13 - m31) / s
            self.np[0] = (m12 + m21) / s
            self.np[1] = 0.25 * s
            self.np[2] = (m23 + m32) / s

        else:
            s = 2.0 * math.sqrt(1.0 + m33 - m11 - m22)

            self.np[3] = (m21 - m12) / s
            self.np[0] = (m13 + m31) / s
            self.np[1] = (m23 + m32) / s
            self.np[2] = 0.25 * s

    def setFromUnitVectors(self, vFrom, vTo):
        global _v1

        # // assumes direction vectors vFrom and vTo are normalized
        EPS = 0.000001
        r = vFrom.dot(vTo) + 1

        if r < EPS:
            r = 0
            if abs(vFrom.x) > abs(vFrom.z):
                _v1.set(- vFrom.y, vFrom.x, 0)
            else:
                _v1.set(0, - vFrom.z, vFrom.y)
        else:
            _v1.crossVectors(vFrom, vTo)

        self.np[0:3] = _v1.np[:]
        self.np[3] = r

        return self.normalize()

    def angleTo(self, q):
        return 2 * math.acos(abs(_Math.clamp(self.dot(q), - 1, 1)))

    def rotateTowards(self, q, step):
        angle = self.angleTo(q)

        if angle == 0:
            return self

        t = min(1, step / angle)

        self.slerp(q, t)

        return self

    def inverse(self):
        # quaternion is assumed to have unit  length
        return self.conjugate()

    def conjugate(self):
        _temp[0] = -1
        _temp[1] = -1
        _temp[2] = -1
        _temp[3] = 1

        self.np *= _temp

        if self.onChangeCallback:
            self.onChangeCallback(self)

        self.updated = True
        return self

    def dot(self, v ):
        global _temp
        _temp = self.np * v.np
        return np.sum(_temp)

    def lengthSq(self):
        global _temp
        _temp = self.np * self.np
        return np.sum(_temp)

    def length(self):
        return math.sqrt(self.lengthSq())

    def normalize(self):
        l = self.length()

        if l == 0:
            self.np[0] = 0
            self.np[1] = 0
            self.np[2] = 0
            self.np[3] = 1
        else:
            l = 1 / l
            self.np *= l

        if self.onChangeCallback:
            self.onChangeCallback(self)

        self.updated = True
        return self

    def multiply(self, q, p=None):
        if p is not None:
            print('THREE.Quaternion: .multiply() now only accepts one argument. Use .multiplyQuaternions( a, b ) instead.')
            return self.multiplyQuaternions(q, p)

        return self.multiplyQuaternions(self, q)

    def premultiply(self, q):
        return self.multiplyQuaternions(q, self)

    def multiplyQuaternions(self, a, b):
        global _cython

        if _cython:
            cQuaternion_multiplyQuaternions(self, a, b)
        else:
            self._multiplyQuaternions(a, b)

        if self.onChangeCallback:
            self.onChangeCallback(self)

        self.updated = True
        return self

    def _multiplyQuaternions(self, a, b):
        # // from http://www.euclideanspace.com/maths/algebra/realNormedAlgebra/quaternions/code/index.htm
        global _temp

        # qax = a.np[0]; qay = a.np[1]; qaz = a.np[2]; qaw = a.np[3]
        # qbx = b.np[0]; qby = b.np[1]; qbz = b.np[2]; qbw = b.np[3]

        # self.np[0] = qax * qbw + qaw * qbx + qay * qbz - qaz * qby
        _temp[0] = a.np[3]
        _temp[1] = a.np[2]
        _temp[2] = a.np[1]
        _temp[3] = a.np[0]
        _temp *= b.np
        x = _temp[3] + _temp[0] + _temp[2] - _temp[1]

        # self.np[1] = qay * qbw + qaw * qby + qaz * qbx - qax * qbz
        _temp[0] = a.np[2]
        _temp[1] = a.np[3]
        _temp[2] = a.np[0]
        _temp[3] = a.np[1]
        _temp *= b.np
        y = _temp[3] + _temp[1] + _temp[0] - _temp[2]

        # self.np[2] = qaz * qbw + qaw * qbz + qax * qby - qay * qbx
        _temp[0] = a.np[1]
        _temp[1] = a.np[0]
        _temp[2] = a.np[3]
        _temp[3] = a.np[2]
        _temp *= b.np
        z = _temp[3] + _temp[2] + _temp[1] - _temp[0]

        # self.np[3] = qaw * qbw - qax * qbx - qay * qby - qaz * qbz
        _temp[:] = a.np[:]
        _temp *= b.np
        w = _temp[3] - _temp[0] - _temp[1] - _temp[2]

        self.np[0] = x
        self.np[1] = y
        self.np[2] = z
        self.np[3] = w

    def slerp2(self, qb, t):
        if t == 0:
            return self
        if t == 1:
            return self.copy(qb)

        x = self.np[0]; y = self.np[1]; z = self.np[2]; w = self.np[3]

        # // http://www.euclideanspace.com/maths/algebra/realNormedAlgebra/quaternions/slerp/

        cosHalfTheta = w * qb.np[3] + x * qb.np[0] + y * qb.np[1] + z * qb.np[2]

        if cosHalfTheta < 0:
            self.np[3] = - qb.np[3]
            self.np[0] = - qb.np[0]
            self.np[1] = - qb.np[1]
            self.np[2] = - qb.np[2]

            cosHalfTheta = - cosHalfTheta
        else:
            self.copy(qb)

        if cosHalfTheta >= 1.0:
            self.np[3] = w
            self.np[0] = x
            self.np[1] = y
            self.np[2] = z

            self.updated = True
            return self

        sqrSinHalfTheta = 1.0 - cosHalfTheta * cosHalfTheta

        if sqrSinHalfTheta <= Number.EPSILON < 0.001:
            s = 1 - t
            self.np[3] = s * w + t * self.np[3]
            self.np[0] = s * x + t * self.np[0]
            self.np[1] = s * y + t * self.np[1]
            self.np[2] = s * z + t * self.np[2]

            return self.normalize()

        sinHalfTheta = math.sqrt(sqrSinHalfTheta)
        halfTheta = math.atan2(sinHalfTheta, cosHalfTheta)
        ratioA = math.sin((1 - t) * halfTheta) / sinHalfTheta
        ratioB = math.sin(t * halfTheta) / sinHalfTheta

        self.np[3] = (w * ratioA + self.np[3] * ratioB)
        self.np[0] = (x * ratioA + self.np[0] * ratioB)
        self.np[1] = (y * ratioA + self.np[1] * ratioB)
        self.np[2] = (z * ratioA + self.np[2] * ratioB)

        if self.onChangeCallback:
            self.onChangeCallback(self)

        self.updated = True
        return self

    def equals(self, quaternion):
        return quaternion.np == self.np

    def fromArray(self, array, offset=0):
        self.np[:] = array[offset:offset + 4]

        if self.onChangeCallback:
            self.onChangeCallback(self)

        self.updated = True
        return self

    def toArray(self, array=None, offset=0):
        if array is None:
            array = []

        array[offset:offset + 4] = self.np[:]

        return array
            
    def onChange(self, callback):
        self.onChangeCallback = callback
        return self
