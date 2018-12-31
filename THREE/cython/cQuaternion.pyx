#cython: cdivision=True
#cython: boundscheck=False
#cython: wraparound=False

"""
 * @author tschw
"""
cimport cython

import numpy as np
cimport numpy as np
from libc.math cimport sqrt, atan2, sin, asin
from libc.string cimport memcpy, memcmp

_temp = np.zeros(4, np.float32)


cpdef cQuaternion_setFromRotationMatrix(self, m):
    # // http://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToQuaternion/index.htm
    # // assumes the upper 3x3 of m is a pure rotation matrix (i.e, unscaled)

    cdef np.ndarray[np.float32_t, ndim=1] te = m.elements
    cdef np.ndarray[np.float32_t, ndim=1] se = self.np

    cdef np.float32_t m11 = te[0]
    cdef np.float32_t m12 = te[4]
    cdef np.float32_t m13 = te[8]
    cdef np.float32_t m21 = te[1]
    cdef np.float32_t m22 = te[5]
    cdef np.float32_t m23 = te[9]
    cdef np.float32_t m31 = te[2]
    cdef np.float32_t m32 = te[6]
    cdef np.float32_t m33 = te[10]

    cdef np.float32_t trace = m11 + m22 + m33
    cdef np.float32_t s

    if trace > 0:
        s = 0.5 / sqrt(trace + 1.0)

        se[3] = 0.25 / s
        se[0] = (m32 - m23) * s
        se[1] = (m13 - m31) * s
        se[2] = (m21 - m12) * s
    elif m11 > m22 and m11 > m33:
        s = 2.0 * sqrt(1.0 + m11 - m22 - m33)

        se[3] = (m32 - m23) / s
        se[0] = 0.25 * s
        se[1] = (m12 + m21) / s
        se[2] = (m13 + m31) / s

    elif m22 > m33:
        s = 2.0 * sqrt(1.0 + m22 - m11 - m33)

        se[3] = (m13 - m31) / s
        se[0] = (m12 + m21) / s
        se[1] = 0.25 * s
        se[2] = (m23 + m32) / s

    else:
        s = 2.0 * sqrt(1.0 + m33 - m11 - m22)

        se[3] = (m21 - m12) / s
        se[0] = (m13 + m31) / s
        se[1] = (m23 + m32) / s
        se[2] = 0.25 * s

cpdef cQuaternion_multiplyQuaternions(self, a, b):
    # // from http://www.euclideanspace.com/maths/algebra/realNormedAlgebra/quaternions/code/index.htm
    global _temp

    cdef np.ndarray[np.float32_t, ndim=1] anp = a.np
    cdef np.ndarray[np.float32_t, ndim=1] bnp = b.np
    cdef np.ndarray[np.float32_t, ndim=1] snp = self.np

    cdef np.float32_t qax = anp[0]
    cdef np.float32_t qay = anp[1]
    cdef np.float32_t qaz = anp[2]
    cdef np.float32_t qaw = anp[3]
    cdef np.float32_t qbx = bnp[0]
    cdef np.float32_t qby = bnp[1]
    cdef np.float32_t qbz = bnp[2]
    cdef np.float32_t qbw = bnp[3]

    snp[0] = qax * qbw + qaw * qbx + qay * qbz - qaz * qby
    snp[1] = qay * qbw + qaw * qby + qaz * qbx - qax * qbz
    snp[2] = qaz * qbw + qaw * qbz + qax * qby - qay * qbx
    snp[3] = qaw * qbw - qax * qbx - qay * qby - qaz * qbz

"""
Quaternion
"""
cpdef cQuaternion_slerpFlat(np.ndarray[np.float32_t, ndim=1] dst ,
                        int dstOffset,
                        np.ndarray[np.float32_t, ndim=1] src0 ,
                        int srcOffset0,
                        np.ndarray[np.float32_t, ndim=1] src1 ,
                        int srcOffset1,
                        np.float32_t t ):
    # // fuzz-free, array-based Quaternion SLERP operation
    cdef float t1 = t
    cdef np.float32_t x0 = src0[ srcOffset0 + 0 ]
    cdef np.float32_t y0 = src0[ srcOffset0 + 1 ]
    cdef np.float32_t z0 = src0[ srcOffset0 + 2 ]
    cdef np.float32_t w0 = src0[ srcOffset0 + 3 ]

    cdef np.float32_t x1 = src1[ srcOffset1 + 0 ]
    cdef np.float32_t y1 = src1[ srcOffset1 + 1 ]
    cdef np.float32_t z1 = src1[ srcOffset1 + 2 ]
    cdef np.float32_t w1 = src1[ srcOffset1 + 3 ]

    cdef np.float32_t s
    cdef np.float32_t cos
    cdef int dir
    cdef np.float32_t sqrSin
    cdef np.float32_t sin1
    cdef np.float32_t len
    cdef np.float32_t tDir
    cdef np.float32_t f

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
