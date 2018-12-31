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

cpdef cUpdateValueArrayElement(self, value, long long buffer, long long element):
    """
    Update a single uniform in an array of uniforms
    :param self:
    :param value:
    :param buffer:
    :param element:
    :return:
    """
    cdef long long offset = self.offset
    cdef long long element_size = self.element_size
    cdef np.ndarray[np.float32_t, ndim=1] data = value.elements

    memcpy(<void *>(buffer + offset + element * element_size), <void *>&data[0], element_size)

cpdef cUpdateValueMat3ArrayElement(self, value, long long buffer, long long element):
    """
    Mat3 are stored as 3 rows of vec4 in STD140
    """
    cdef long long offset = self.offset
    cdef long long element_size = self.element_size
    cdef long long start = buffer + offset + element * element_size
    #cdef long long data = value.elements.ctypes.data
    cdef np.ndarray[np.float32_t, ndim=1] data = value.elements

    memcpy(<void *>start, <void *>&data[0], 12)
    memcpy(<void *>(start + 16), <void *>&data[3], 12)
    memcpy(<void *>(start + 32), <void *>&data[6], 12)
