"""
 * @author tschw
"""
#cython: cdivision=True
cimport cython

import numpy as np
cimport numpy as np
from libc.math cimport sqrt, atan2, sin


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


@cython.cdivision(True)
def cVector3_applyMatrix4(np.ndarray[double, ndim=1] vector3, np.ndarray[double, ndim=1] matrix4):
        cdef double x = vector3[0]
        cdef double y = vector3[1]
        cdef double z = vector3[2]

        cdef double w = 1 / ( matrix4[ 3 ] * x + matrix4[ 7 ] * y + matrix4[ 11 ] * z + matrix4[ 15 ] );

        vector3[0] = ( matrix4[ 0 ] * x + matrix4[ 4 ] * y + matrix4[ 8 ]  * z + matrix4[ 12 ] ) * w;
        vector3[1] = ( matrix4[ 1 ] * x + matrix4[ 5 ] * y + matrix4[ 9 ]  * z + matrix4[ 13 ] ) * w;
        vector3[2] = ( matrix4[ 2 ] * x + matrix4[ 6 ] * y + matrix4[ 10 ] * z + matrix4[ 14 ] ) * w;

@cython.cdivision(True)
def decompose(np.ndarray[double, ndim=1] te, position, quaternion, scale):
    vector = THREE.Vector3()
    matrix = Matrix4()

    te = self.elements

    sx = vector.set(te[0], te[1], te[2]).length()
    sy = vector.set(te[4], te[5], te[6]).length()
    sz = vector.set(te[8], te[9], te[10]).length()

    # // if determine is negative, we need to invert one scale
    det = self.determinant()
    if det < 0:
        sx = - sx

    position.x = te[12]
    position.y = te[13]
    position.z = te[14]

    # // scale the rotation part
    matrix.copy(self)

    invSX = 1 / sx
    invSY = 1 / sy
    invSZ = 1 / sz

    matrix.elements[0] *= invSX
    matrix.elements[1] *= invSX
    matrix.elements[2] *= invSX

    matrix.elements[4] *= invSY
    matrix.elements[5] *= invSY
    matrix.elements[6] *= invSY

    matrix.elements[8] *= invSZ
    matrix.elements[9] *= invSZ
    matrix.elements[10] *= invSZ

    quaternion.setFromRotationMatrix(matrix)

    scale.x = sx
    scale.y = sy
    scale.z = sz

    return self
