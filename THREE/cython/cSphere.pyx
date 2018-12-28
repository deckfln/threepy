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

from THREE.cython.cVector3 import cVector3_applyMatrix4
from THREE.cython.cMatrix4 import cMatrix4_getMaxScaleOnAxis


cpdef cSphere_isIncludedIn(self, sphere):
    cdef float r = self.radius
    cdef float r1 = sphere.radius
    cdef np.ndarray[np.float32_t, ndim=1] c = self.center.np
    cdef np.ndarray[np.float32_t, ndim=1] c1 = sphere.center.np
    cdef np.float32_t rx, ry, rz

    rx = c[0] - c1[0]
    ry = c[1] - c1[1]
    rz = c[2] - c1[2]
    d = sqrt(rx*rx + ry*ry + rz*rz) + r
    return d < r1

cpdef cSphere_applyMatrix4(object self, object matrix):
    cdef np.ndarray[np.float32_t, ndim=1] center = self.center.np
    cdef np.ndarray[np.float32_t, ndim=1] matrix4 = matrix.elements
    cdef float radius = self.radius

    #cVector3_applyMatrix4(self.center, matrix)
    cdef np.float32_t x = center[0]
    cdef np.float32_t y = center[1]
    cdef np.float32_t z = center[2]

    cdef np.float32_t w = 1 / ( matrix4[ 3 ] * x + matrix4[ 7 ] * y + matrix4[ 11 ] * z + matrix4[ 15 ] );

    center[0] = ( matrix4[ 0 ] * x + matrix4[ 4 ] * y + matrix4[ 8 ]  * z + matrix4[ 12 ] ) * w;
    center[1] = ( matrix4[ 1 ] * x + matrix4[ 5 ] * y + matrix4[ 9 ]  * z + matrix4[ 13 ] ) * w;
    center[2] = ( matrix4[ 2 ] * x + matrix4[ 6 ] * y + matrix4[ 10 ] * z + matrix4[ 14 ] ) * w;

    #radius *= cMatrix4_getMaxScaleOnAxis(matrix4)
    x = matrix4[0] * matrix4[0] + matrix4[1] * matrix4[1] + matrix4[2] * matrix4[2]
    y = matrix4[4] * matrix4[4] + matrix4[5] * matrix4[5] + matrix4[6] * matrix4[6]
    z = matrix4[8] * matrix4[8] + matrix4[9] * matrix4[9] + matrix4[10] * matrix4[10]

    self.radius = radius * sqrt(max(x, y, z))
