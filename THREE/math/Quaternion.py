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

cython = True
_v1 = Vector3()

class Quaternion:
    def __init__(self, x=0, y=0, z=0, w=1 ):
        self._x = x
        self._y = y
        self._z = z
        self._w = w
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

    def setW(self, w):
        self._order = w
        if self.onChangeCallback:
            self.onChangeCallback(self)

    def getX(self):
        return self._x

    def getY(self):
        return self._y

    def getZ(self):
        return self._z

    def getW(self):
        return self._w

    x = property(getX, setX)
    y = property(getY, setY)
    z = property(getZ, setZ)
    w = property(getW, setW)
        
    def slerp(self, qa, qb, qm=None, t=None ):
        if qm is None:
            return self._slerp(qa, qb)
        else:
            return qm.copy( qa ).slerp( qb, t )

    def slerpFlat(self, dst, dstOffset, src0, srcOffset0, src1, srcOffset1, t ):
        if cython:
            cQuaternion_slerpFlat(dst, dstOffset, src0, srcOffset0, src1, srcOffset1, t )
        else:
            self._pslerpFlat(dst, dstOffset, src0, srcOffset0, src1, srcOffset1, t)

    def _pslerpFlat(self, dst, dstOffset, src0, srcOffset0, src1, srcOffset1, t ):
        # // fuzz-free, array-based Quaternion SLERP operation

        x0 = src0[ srcOffset0 + 0 ]
        y0 = src0[ srcOffset0 + 1 ]
        z0 = src0[ srcOffset0 + 2 ]
        w0 = src0[ srcOffset0 + 3 ]

        x1 = src1[ srcOffset1 + 0 ]
        y1 = src1[ srcOffset1 + 1 ]
        z1 = src1[ srcOffset1 + 2 ]
        w1 = src1[ srcOffset1 + 3 ]

        if w0 != w1 or x0 != x1 or y0 != y1 or z0 != z1:
            s = 1 - t
            cos = x0 * x1 + y0 * y1 + z0 * z1 + w0 * w1
            dir = -1
            if cos >= 0:
                dir = 1
            sqrSin = 1 - cos * cos

            # // Skip the Slerp for tiny steps to avoid numeric problems:
            if sqrSin > Number.EPSILON:
                sin = math.sqrt( sqrSin )
                len = math.atan2( sin, cos * dir )

                s = math.sin( s * len ) / sin
                t = math.sin( t * len ) / sin

            tDir = t * dir

            x0 = x0 * s + x1 * tDir
            y0 = y0 * s + y1 * tDir
            z0 = z0 * s + z1 * tDir
            w0 = w0 * s + w1 * tDir

            # // Normalize in case we just did a lerp:
            if s == 1 - t:
                f = 1 / math.sqrt( x0 * x0 + y0 * y0 + z0 * z0 + w0 * w0 )
                
                x0 *= f
                y0 *= f
                z0 *= f
                w0 *= f

        dst[ dstOffset ] = x0
        dst[ dstOffset + 1 ] = y0
        dst[ dstOffset + 2 ] = z0
        dst[ dstOffset + 3 ] = w0

    def set(self, x, y, z, w ):
        self._x = x
        self._y = y
        self._z = z
        self._w = w

        if self.onChangeCallback:
            self.onChangeCallback(self)

        return self

    def clone(self):
        return type(self)( self._x, self._y, self._z, self._w )

    def copy(self, quaternion ):
        self._x = quaternion._x
        self._y = quaternion._y
        self._z = quaternion._z
        self._w = quaternion._w

        if self.onChangeCallback:
            self.onChangeCallback(self)
        
        return self

    def setFromEuler(self, euler, update=False ):
        if not ( euler and euler.isEuler):
            print( 'THREE.Quaternion: .setFromEuler() now expects an Euler rotation rather than a Vector3 and order.' )

        x = euler._x; y = euler._y; z = euler._z; order = euler.order

        # // http://www.mathworks.com/matlabcentral/fileexchange/
        # //     20696-function-to-convert-between-dcm-euler-angles-quaternions-and-euler-vectors/
        # //    content/SpinCalc.m

        cos = math.cos
        sin = math.sin

        c1 = cos( x / 2 )
        c2 = cos( y / 2 )
        c3 = cos( z / 2 )

        s1 = sin( x / 2 )
        s2 = sin( y / 2 )
        s3 = sin( z / 2 )

        if order == 'XYZ':
            self._x = s1 * c2 * c3 + c1 * s2 * s3
            self._y = c1 * s2 * c3 - s1 * c2 * s3
            self._z = c1 * c2 * s3 + s1 * s2 * c3
            self._w = c1 * c2 * c3 - s1 * s2 * s3
        elif order == 'YXZ':
            self._x = s1 * c2 * c3 + c1 * s2 * s3
            self._y = c1 * s2 * c3 - s1 * c2 * s3
            self._z = c1 * c2 * s3 - s1 * s2 * c3
            self._w = c1 * c2 * c3 + s1 * s2 * s3
        elif order == 'ZXY':
            self._x = s1 * c2 * c3 - c1 * s2 * s3
            self._y = c1 * s2 * c3 + s1 * c2 * s3
            self._z = c1 * c2 * s3 + s1 * s2 * c3
            self._w = c1 * c2 * c3 - s1 * s2 * s3
        elif order == 'ZYX':
            self._x = s1 * c2 * c3 - c1 * s2 * s3
            self._y = c1 * s2 * c3 + s1 * c2 * s3
            self._z = c1 * c2 * s3 - s1 * s2 * c3
            self._w = c1 * c2 * c3 + s1 * s2 * s3
        elif order == 'YZX':
            self._x = s1 * c2 * c3 + c1 * s2 * s3
            self._y = c1 * s2 * c3 + s1 * c2 * s3
            self._z = c1 * c2 * s3 - s1 * s2 * c3
            self._w = c1 * c2 * c3 - s1 * s2 * s3
        elif order == 'XZY':
            self._x = s1 * c2 * c3 - c1 * s2 * s3
            self._y = c1 * s2 * c3 - s1 * c2 * s3
            self._z = c1 * c2 * s3 + s1 * s2 * c3
            self._w = c1 * c2 * c3 + s1 * s2 * s3

        if update:
            self.onChangeCallback(self)

        return self

    def setFromAxisAngle(self, axis, angle ):
        # // http://www.euclideanspace.com/maths/geometry/rotations/conversions/angleToQuaternion/index.htm
        # // assumes axis is normalized
        halfAngle = angle / 2; s = math.sin( halfAngle )

        self._x = axis.x * s
        self._y = axis.y * s
        self._z = axis.z * s
        self._w = math.cos( halfAngle )

        if self.onChangeCallback:
            self.onChangeCallback(self)

        return self

    def setFromRotationMatrix(self, m ):
        # // http://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToQuaternion/index.htm
        # // assumes the upper 3x3 of m is a pure rotation matrix (i.e, unscaled)
        te = m.elements
        m11 = te[ 0 ]; m12 = te[ 4 ]; m13 = te[ 8 ]
        m21 = te[ 1 ]; m22 = te[ 5 ]; m23 = te[ 9 ]
        m31 = te[ 2 ]; m32 = te[ 6 ]; m33 = te[ 10 ]

        trace = m11 + m22 + m33

        if trace > 0:
            s = 0.5 / math.sqrt( trace + 1.0 )
            self._w = 0.25 / s
            self._x = ( m32 - m23 ) * s
            self._y = ( m13 - m31 ) * s
            self._z = ( m21 - m12 ) * s
        elif m11 > m22 and m11 > m33:
            s = 2.0 * math.sqrt( 1.0 + m11 - m22 - m33 )
            self._w = ( m32 - m23 ) / s
            self._x = 0.25 * s
            self._y = ( m12 + m21 ) / s
            self._z = ( m13 + m31 ) / s
        elif m22 > m33:
            s = 2.0 * math.sqrt( 1.0 + m22 - m11 - m33 )
            self._w = ( m13 - m31 ) / s
            self._x = ( m12 + m21 ) / s
            self._y = 0.25 * s
            self._z = ( m23 + m32 ) / s
        else:
            s = 2.0 * math.sqrt( 1.0 + m33 - m11 - m22 )
            self._w = ( m21 - m12 ) / s
            self._x = ( m13 + m31 ) / s
            self._y = ( m23 + m32 ) / s
            self._z = 0.25 * s

        if self.onChangeCallback:
            self.onChangeCallback(self)

        return self

    def setFromUnitVectors(self, vFrom, vTo):
        global _v1

        # // assumes direction vectors vFrom and vTo are normalized
        EPS = 0.000001
        r = vFrom.dot( vTo ) + 1

        if r < EPS:
            r = 0
            if abs( vFrom.x ) > abs( vFrom.z ):
                _v1.set( - vFrom.y, vFrom.x, 0 )
            else:
                _v1.set( 0, - vFrom.z, vFrom.y )
        else:
            _v1.crossVectors( vFrom, vTo )

        self._x = _v1.x
        self._y = _v1.y
        self._z = _v1.z
        self._w = r

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
        self._x *= - 1
        self._y *= - 1
        self._z *= - 1

        if self.onChangeCallback:
            self.onChangeCallback(self)

        return self

    def dot(self, v ):
        return self._x * v._x + self._y * v._y + self._z * v._z + self._w * v._w

    def lengthSq(self):
        return self._x * self._x + self._y * self._y + self._z * self._z + self._w * self._w

    def length(self):
        return math.sqrt( self._x * self._x + self._y * self._y + self._z * self._z + self._w * self._w )

    def normalize(self):
        l = self.length()

        if l == 0:
            self._x = 0
            self._y = 0
            self._z = 0
            self._w = 1
        else:
            l = 1 / l
            self._x = self._x * l
            self._y = self._y * l
            self._z = self._z * l
            self._w = self._w * l

        if self.onChangeCallback:
            self.onChangeCallback(self)

        return self

    def multiply(self, q, p=None ):
        if p is not None:
            print( 'THREE.Quaternion: .multiply() now only accepts one argument. Use .multiplyQuaternions( a, b ) instead.' )
            return self.multiplyQuaternions( q, p )

        return self.multiplyQuaternions( self, q )

    def premultiply(self, q ):
        return self.multiplyQuaternions( q, self )

    def multiplyQuaternions(self, a, b ):
        # // from http://www.euclideanspace.com/maths/algebra/realNormedAlgebra/quaternions/code/index.htm

        qax = a._x; qay = a._y; qaz = a._z; qaw = a._w
        qbx = b._x; qby = b._y; qbz = b._z; qbw = b._w

        self._x = qax * qbw + qaw * qbx + qay * qbz - qaz * qby
        self._y = qay * qbw + qaw * qby + qaz * qbx - qax * qbz
        self._z = qaz * qbw + qaw * qbz + qax * qby - qay * qbx
        self._w = qaw * qbw - qax * qbx - qay * qby - qaz * qbz

        if self.onChangeCallback:
            self.onChangeCallback(self)

        return self

    def slerp2(self, qb, t ):
        if t == 0:
            return self
        if t == 1:
            return self.copy( qb )

        x = self._x; y = self._y; z = self._z; w = self._w

        # // http://www.euclideanspace.com/maths/algebra/realNormedAlgebra/quaternions/slerp/

        cosHalfTheta = w * qb._w + x * qb._x + y * qb._y + z * qb._z

        if cosHalfTheta < 0:
            self._w = - qb._w
            self._x = - qb._x
            self._y = - qb._y
            self._z = - qb._z

            cosHalfTheta = - cosHalfTheta
        else:
            self.copy( qb )

        if cosHalfTheta >= 1.0:
            self._w = w
            self._x = x
            self._y = y
            self._z = z

            return self

        sqrSinHalfTheta = 1.0 - cosHalfTheta * cosHalfTheta

        if sqrSinHalfTheta <= Number.EPSILON < 0.001:
            s = 1 - t
            self._w = s * w + t * self._w
            self._x = s * x + t * self._x
            self._y = s * y + t * self._y
            self._z = s * z + t * self._z

            return self.normalize()

        sinHalfTheta = math.sqrt(sqrSinHalfTheta)
        halfTheta = math.atan2( sinHalfTheta, cosHalfTheta )
        ratioA = math.sin( ( 1 - t ) * halfTheta ) / sinHalfTheta
        ratioB = math.sin( t * halfTheta ) / sinHalfTheta

        self._w = ( w * ratioA + self._w * ratioB )
        self._x = ( x * ratioA + self._x * ratioB )
        self._y = ( y * ratioA + self._y * ratioB )
        self._z = ( z * ratioA + self._z * ratioB )

        if self.onChangeCallback:
            self.onChangeCallback(self)

        return self

    def equals(self, quaternion ):
        return quaternion._x == self._x and quaternion._y == self._y and quaternion._z == self._z and quaternion._w == self._w

    def fromArray(self, array, offset=0 ):
        self._x = array[ offset ]
        self._y = array[ offset + 1 ]
        self._z = array[ offset + 2 ]
        self._w = array[ offset + 3 ]

        if self.onChangeCallback:
            self.onChangeCallback(self)

        return self

    def toArray(self, array=None, offset=0 ):
        if array is None:
            array = []

        array[ offset ] = self._x
        array[ offset + 1 ] = self._y
        array[ offset + 2 ] = self._z
        array[ offset + 3 ] = self._w

        return array
            
    def onChange(self, callback):
        self.onChangeCallback = callback
        return self