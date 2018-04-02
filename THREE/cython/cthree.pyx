"""
 * @author tschw
"""
#cython: cdivision=True
cimport cython

import numpy as np
cimport numpy as np
from libc.math cimport sqrt, atan2, sin, asin

"""
"""
@cython.cdivision(True)
def cinterpolate_(np.ndarray[float, ndim=1] result, np.ndarray[float, ndim=1] values, int stride, int i1, double t0, double t, double t1 ):
    cdef int offset1 = i1 * stride
    cdef int offset0 = offset1 - stride

    cdef double weight1 = ( t - t0 ) / ( t1 - t0 )
    cdef double weight0 = 1 - weight1
    cdef float a
    cdef float b
    cdef int i

    for i in range(stride):
        a = values[ offset0 + i ]
        b = values[ offset1 + i ]
        result[ i ] = a * weight0 + b * weight1

    return result

def c_Matrix4_makeRotationFromQuaternion(np.ndarray[double, ndim=1] te, double x, double y, double z, double w):
    cdef double x2 = x + x
    cdef double y2 = y + y
    cdef double z2 = z + z
    cdef double xx = x * x2
    cdef double xy = x * y2
    cdef double xz = x * z2
    cdef double yy = y * y2
    cdef double yz = y * z2
    cdef double zz = z * z2
    cdef double wx = w * x2
    cdef double wy = w * y2
    cdef double wz = w * z2

    te[0] = 1 - (yy + zz)
    te[4] = xy - wz
    te[8] = xz + wy

    te[1] = xy + wz
    te[5] = 1 - (xx + zz)
    te[9] = yz - wx

    te[2] = xz - wy
    te[6] = yz + wx
    te[10] = 1 - (xx + yy)

    # // last column
    te[3] = 0
    te[7] = 0
    te[11] = 0

    # // bottom row
    te[12] = 0
    te[13] = 0
    te[14] = 0
    te[15] = 1


def cMatrix4_multiplyMatrices(np.ndarray[double, ndim=1] te, np.ndarray[double, ndim=1] ae, np.ndarray[double, ndim=1] be):
        cdef double a11 = ae[0]
        cdef double  a12 = ae[4]
        cdef double  a13 = ae[8]
        cdef double  a14 = ae[12]
        cdef double a21 = ae[1]
        cdef double  a22 = ae[5]
        cdef double  a23 = ae[9]
        cdef double  a24 = ae[13]
        cdef double a31 = ae[2]
        cdef double  a32 = ae[6]
        cdef double  a33 = ae[10]
        cdef double  a34 = ae[14]
        cdef double a41 = ae[3]
        cdef double  a42 = ae[7]
        cdef double  a43 = ae[11]
        cdef double  a44 = ae[15]

        cdef double b11 = be[0]
        cdef double  b12 = be[4]
        cdef double  b13 = be[8]
        cdef double  b14 = be[12]
        cdef double b21 = be[1]
        cdef double  b22 = be[5]
        cdef double  b23 = be[9]
        cdef double  b24 = be[13]
        cdef double b31 = be[2]
        cdef double  b32 = be[6]
        cdef double  b33 = be[10]
        cdef double  b34 = be[14]
        cdef double b41 = be[3]
        cdef double  b42 = be[7]
        cdef double  b43 = be[11]
        cdef double  b44 = be[15]

        te[0] = a11 * b11 + a12 * b21 + a13 * b31 + a14 * b41
        te[4] = a11 * b12 + a12 * b22 + a13 * b32 + a14 * b42
        te[8] = a11 * b13 + a12 * b23 + a13 * b33 + a14 * b43
        te[12] = a11 * b14 + a12 * b24 + a13 * b34 + a14 * b44

        te[1] = a21 * b11 + a22 * b21 + a23 * b31 + a24 * b41
        te[5] = a21 * b12 + a22 * b22 + a23 * b32 + a24 * b42
        te[9] = a21 * b13 + a22 * b23 + a23 * b33 + a24 * b43
        te[13] = a21 * b14 + a22 * b24 + a23 * b34 + a24 * b44

        te[2] = a31 * b11 + a32 * b21 + a33 * b31 + a34 * b41
        te[6] = a31 * b12 + a32 * b22 + a33 * b32 + a34 * b42
        te[10] = a31 * b13 + a32 * b23 + a33 * b33 + a34 * b43
        te[14] = a31 * b14 + a32 * b24 + a33 * b34 + a34 * b44

        te[3] = a41 * b11 + a42 * b21 + a43 * b31 + a44 * b41
        te[7] = a41 * b12 + a42 * b22 + a43 * b32 + a44 * b42
        te[11] = a41 * b13 + a42 * b23 + a43 * b33 + a44 * b43
        te[15] = a41 * b14 + a42 * b24 + a43 * b34 + a44 * b44

def cMatrix4_scale(np.ndarray[double, ndim=1] te, np.ndarray[double, ndim=1] v):
    te[0] *= v[0]
    te[4] *= v[1]
    te[8] *= v[2]
    te[1] *= v[0]
    te[5] *= v[1]
    te[9] *= v[2]
    te[2] *= v[0]
    te[6] *= v[1]
    te[10] *= v[2]
    te[3] *= v[0]
    te[7] *= v[1]
    te[11] *= v[2]

def cMatrix4_setPosition(np.ndarray[double, ndim=1] te, np.ndarray[double, ndim=1] v):
    te[12] = v[0]
    te[13] = v[1]
    te[14] = v[2]

def cMatrix4_compose(np.ndarray[double, ndim=1] te, np.ndarray[double, ndim=1] position,np.ndarray[double, ndim=1] scale, double x, double y, double z, double w):
    cdef double x2 = x + x
    cdef double y2 = y + y
    cdef double z2 = z + z
    cdef double xx = x * x2
    cdef double xy = x * y2
    cdef double xz = x * z2
    cdef double yy = y * y2
    cdef double yz = y * z2
    cdef double zz = z * z2
    cdef double wx = w * x2
    cdef double wy = w * y2
    cdef double wz = w * z2

    cdef double xs = scale[0]
    cdef double ys = scale[1]
    cdef double zs = scale[2]

    te[0] = (1 - (yy + zz)) * xs
    te[4] = (xy - wz) * ys
    te[8] = (xz + wy) * zs

    te[1] = (xy + wz) * xs
    te[5] = (1 - (xx + zz)) * ys
    te[9] = (yz - wx) * ys

    te[2] = (xz - wy) * xs
    te[6] = (yz + wx) * ys
    te[10] = (1 - (xx + yy)) * zs

    # // last column
    te[3] = 0
    te[7] = 0
    te[11] = 0

    # // bottom row
    te[15] = 1

    te[12] = position[0]
    te[13] = position[1]
    te[14] = position[2]

@cython.cdivision(True)
def cQuaternion_slerpFlat(np.ndarray[float, ndim=1] dst, int dstOffset, np.ndarray[float, ndim=1] src0, int srcOffset0, np.ndarray[float, ndim=1] src1, int srcOffset1, float  t ):
    # // fuzz-free, array-based Quaternion SLERP operation
    cdef float t1 = t
    cdef float x0 = src0[ srcOffset0 + 0 ]
    cdef float y0 = src0[ srcOffset0 + 1 ]
    cdef float z0 = src0[ srcOffset0 + 2 ]
    cdef float w0 = src0[ srcOffset0 + 3 ]

    cdef float x1 = src1[ srcOffset1 + 0 ]
    cdef float y1 = src1[ srcOffset1 + 1 ]
    cdef float z1 = src1[ srcOffset1 + 2 ]
    cdef float w1 = src1[ srcOffset1 + 3 ]

    cdef float s
    cdef float cos
    cdef int dir
    cdef float sqrSin
    cdef float sin1
    cdef float len
    cdef float tDir
    cdef float f

    if w0 != w1 or x0 != x1 or y0 != y1 or z0 != z1:
        s = 1 - t1
        cos = x0 * x1 + y0 * y1 + z0 * z1 + w0 * w1
        dir = -1
        if cos >= 0:
            dir = 1
        sqrSin = 1 - cos * cos

        # // Skip the Slerp for tiny steps to avoid numeric problems:
        if sqrSin > 2.220446049250313e-16:
            sin1 = sqrt( sqrSin )
            len = atan2( sin1, cos * dir )

            s = sin( s * len ) / sin1
            t = sin( t1 * len ) / sin1

        tDir = t1 * dir

        x0 = x0 * s + x1 * tDir
        y0 = y0 * s + y1 * tDir
        z0 = z0 * s + z1 * tDir
        w0 = w0 * s + w1 * tDir

        # // Normalize in case we just did a lerp:
        if s == 1 - t1:
            f = 1 / sqrt( x0 * x0 + y0 * y0 + z0 * z0 + w0 * w0 )

            x0 *= f
            y0 *= f
            z0 *= f
            w0 *= f

    dst[ dstOffset ] = x0
    dst[ dstOffset + 1 ] = y0
    dst[ dstOffset + 2 ] = z0
    dst[ dstOffset + 3 ] = w0


def cMath_clamp( double value, double mi, double mx ):
    if value < mi:
        return mi
    if value > mx:
        return mx
    return value

"""
Vector3
"""
@cython.cdivision(True)
def cVector3_applyMatrix4(np.ndarray[double, ndim=1] vector3, np.ndarray[double, ndim=1] matrix4):
        cdef double x = vector3[0]
        cdef double y = vector3[1]
        cdef double z = vector3[2]

        cdef double w = 1 / ( matrix4[ 3 ] * x + matrix4[ 7 ] * y + matrix4[ 11 ] * z + matrix4[ 15 ] );

        vector3[0] = ( matrix4[ 0 ] * x + matrix4[ 4 ] * y + matrix4[ 8 ]  * z + matrix4[ 12 ] ) * w;
        vector3[1] = ( matrix4[ 1 ] * x + matrix4[ 5 ] * y + matrix4[ 9 ]  * z + matrix4[ 13 ] ) * w;
        vector3[2] = ( matrix4[ 2 ] * x + matrix4[ 6 ] * y + matrix4[ 10 ] * z + matrix4[ 14 ] ) * w;

"""
Euler
"""
def cEuler_setFromRotationMatrix(self, np.ndarray[double, ndim=1] te , str order=None):

    # // assumes the upper 3x3 of m is a pure rotation matrix (i.e, unscaled)

    cdef double m11 = te[ 0 ]
    cdef double m12 = te[ 4 ]
    cdef double m13 = te[ 8 ]
    cdef double m21 = te[ 1 ]
    cdef double m22 = te[ 5 ]
    cdef double m23 = te[ 9 ]
    cdef double m31 = te[ 2 ]
    cdef double m32 = te[ 6 ]
    cdef double  m33 = te[ 10 ]

    order = order or self._order

    if order == 'XYZ':
        self._y = asin(cMath_clamp(m13, - 1, 1))
        if abs(m13) < 0.99999:
            self._x = atan2(- m23, m33)
            self._z = atan2(- m12, m11)
        else:
            self._x = atan2(m32, m22)
            self._z = 0
    elif order == 'YXZ':
        self._x = asin(- cMath_clamp(m23, - 1, 1))
        if abs(m23) < 0.99999:
            self._y = atan2(m13, m33)
            self._z = atan2(m21, m22)
        else:
            self._y = atan2(- m31, m11)
            self._z = 0
    elif order == 'ZXY':
        self._x = asin(cMath_clamp(m32, - 1, 1))
        if abs(m32) < 0.99999:
            self._y = atan2(- m31, m33)
            self._z = atan2(- m12, m22)
        else:
            self._y = 0
            self._z = atan2(m21, m11)
    elif order == 'ZYX':
        self._y = asin(- cMath_clamp(m31, - 1, 1))
        if abs(m31) < 0.99999:
            self._x = atan2(m32, m33)
            self._z = atan2(m21, m11)
        else:
            self._x = 0
            self._z = atan2(- m12, m22)
    elif order == 'YZX':
        self._z = asin(cMath_clamp(m21, - 1, 1))
        if abs(m21) < 0.99999:
            self._x = atan2(- m23, m22)
            self._y = atan2(- m31, m11)
        else:
            self._x = 0
            self._y = atan2(m13, m33)
    elif order == 'XZY':
        self._z = asin(- cMath_clamp(m12, - 1, 1))
        if abs(m12) < 0.99999:
            self._x = atan2(m32, m22)
            self._y = atan2(m13, m11)
        else:
            self._x = atan2(- m23, m33)
            self._y = 0
    else:
        print('THREE.Euler: .setFromRotationMatrix() given unsupported order: ' + order)