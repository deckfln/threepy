#cython: cdivision=True
#cython: boundscheck=False
#cython: wraparound=False

"""
 * @author tschw
"""
cimport cython

import numpy as np
cimport numpy as np
from THREE.cython.cVector3 import cVector3_applyMatrix4, cVector3_getInverse
from THREE.cython.cMatrix4 import cMatrix4_getMaxScaleOnAxis


from libc.math cimport sqrt, atan2, sin, asin
from libc.string cimport memcpy, memcmp


"""
Quaternion
"""
cpdef cQuaternion_slerpFlat(np.ndarray[float, ndim=1] dst ,
                        int dstOffset,
                        np.ndarray[float, ndim=1] src0 ,
                        int srcOffset0,
                        np.ndarray[float, ndim=1] src1 ,
                        int srcOffset1,
                        float  t ):
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


cpdef cMath_clamp( double value, double mi, double mx ):
    if value < mi:
        return mi
    if value > mx:
        return mx
    return value


"""
Euler
"""
cpdef cEuler_setFromRotationMatrix(self,
                                np.ndarray[float, ndim=1] te ,
                                str order=None):

    # // assumes the upper 3x3 of m is a pure rotation matrix (i.e, unscaled)

    cdef float m11 = te[ 0 ]
    cdef float m12 = te[ 4 ]
    cdef float m13 = te[ 8 ]
    cdef float m21 = te[ 1 ]
    cdef float m22 = te[ 5 ]
    cdef float m23 = te[ 9 ]
    cdef float m31 = te[ 2 ]
    cdef float m32 = te[ 6 ]
    cdef float  m33 = te[ 10 ]

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

"""
Plane
"""
cpdef cPlane_distanceToPoint(np.ndarray[np.float32_t, ndim=1] normal ,
                            np.ndarray[np.float32_t, ndim=1] point ,
                            np.float32_t constant ):

    return normal[0] * point[0] + normal[1] * point[1] + normal[2] * point[2] + constant

cpdef cUpdateValueArrayElement(long long buffer, object self, long long element, object value):
    """
    Update a single uniform in an array of uniforms
    :param self:
    :param value:
    :param buffer:
    :param element:
    :return:
    """
    cdef long offset = self.offset
    cdef long element_size = self.element_size
    cdef long long data = value.elements.ctypes.data

    memcpy(<void *>(buffer + offset + element * element_size), <void *>data, element_size)

cpdef cUpdateValueMat3ArrayElement(long long buffer, int offset, long long element, long long element_size, long long data, long long size):
    """
    Mat3 are stored as 3 rows of vec4 in STD140
    """
    cdef long long start = buffer + offset + element * element_size

    memcpy(<void *>start, <void *>data, 12)
    memcpy(<void *>(start + 16), <void *>(data + 12), 12)
    memcpy(<void *>(start + 32), <void *>(data + 24), 12)
