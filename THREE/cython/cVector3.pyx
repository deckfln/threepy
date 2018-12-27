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

cpdef void cVector3_applyMatrix4(self, m):
    cdef np.ndarray[np.float32_t, ndim=1] vector3 = self.np
    cdef np.ndarray[np.float32_t, ndim=1] matrix4 = m.elements

    cdef np.float32_t x = vector3[0]
    cdef np.float32_t y = vector3[1]
    cdef np.float32_t z = vector3[2]

    cdef np.float32_t w = 1 / ( matrix4[ 3 ] * x + matrix4[ 7 ] * y + matrix4[ 11 ] * z + matrix4[ 15 ] );

    vector3[0] = ( matrix4[ 0 ] * x + matrix4[ 4 ] * y + matrix4[ 8 ]  * z + matrix4[ 12 ] ) * w;
    vector3[1] = ( matrix4[ 1 ] * x + matrix4[ 5 ] * y + matrix4[ 9 ]  * z + matrix4[ 13 ] ) * w;
    vector3[2] = ( matrix4[ 2 ] * x + matrix4[ 6 ] * y + matrix4[ 10 ] * z + matrix4[ 14 ] ) * w;

cpdef void cVector3_applyMatrix3(self, m):
    cdef np.ndarray[np.float32_t, ndim=1] this = self.np
    cdef np.ndarray[np.float32_t, ndim=1] e = m.elements

    cdef np.float32_t x = this[0]
    cdef np.float32_t y = this[1]
    cdef np.float32_t z = this[2]

    this[0] = e[ 0 ] * x + e[ 3 ] * y + e[ 6 ] * z
    this[1] = e[ 1 ] * x + e[ 4 ] * y + e[ 7 ] * z
    this[2] = e[ 2 ] * x + e[ 5 ] * y + e[ 8 ] * z

cpdef void cVector3_getInverse(np.ndarray[np.float32_t, ndim=1] te, np.ndarray[np.float32_t, ndim=1] me):
    cdef np.float32_t n11 = me[ 0 ]
    cdef np.float32_t n21 = me[ 1 ]
    cdef np.float32_t n31 = me[ 2 ]
    cdef np.float32_t n12 = me[ 3 ]
    cdef np.float32_t n22 = me[ 4 ]
    cdef np.float32_t n32 = me[ 5 ]
    cdef np.float32_t n13 = me[ 6 ]
    cdef np.float32_t n23 = me[ 7 ]
    cdef np.float32_t n33 = me[ 8 ]

    cdef np.float32_t t11 = n33 * n22 - n32 * n23
    cdef np.float32_t t12 = n32 * n13 - n33 * n12
    cdef np.float32_t t13 = n23 * n12 - n22 * n13

    cdef np.float32_t det = n11 * t11 + n21 * t12 + n31 * t13
    cdef np.float32_t detInv = 1 / det

    if det == 0:
        # raise RuntimeWarning("THREE.Matrix3: .getInverse() can't invert matrix, determinant is 0")
        te[0] = 1
        te[1] = 0
        te[2] = 0
        te[3] = 0
        te[4] = 1
        te[5] = 0
        te[6] = 0
        te[7] = 0
        te[8] = 1
    else:
        detInv = 1 / det
        te[ 0 ] = t11 * detInv
        te[ 1 ] = ( n31 * n23 - n33 * n21 ) * detInv
        te[ 2 ] = ( n32 * n21 - n31 * n22 ) * detInv

        te[ 3 ] = t12 * detInv
        te[ 4 ] = ( n33 * n11 - n31 * n13 ) * detInv
        te[ 5 ] = ( n31 * n12 - n32 * n11 ) * detInv

        te[ 6 ] = t13 * detInv
        te[ 7 ] = ( n21 * n13 - n23 * n11 ) * detInv
        te[ 8 ] = ( n22 * n11 - n21 * n12 ) * detInv

cpdef void cVector3_lerp(np.ndarray[np.float32_t, ndim=1] self, np.ndarray[np.float32_t, ndim=1] v, float alpha):
    self[0] += ( v[0] - self[0] ) * alpha
    self[1] += ( v[1] - self[1] ) * alpha
    self[2] += ( v[2] - self[2] ) * alpha

cpdef void cVector3_copy(self, v):
    cdef np.ndarray[np.float32_t, ndim=1] s = self.np
    cdef np.ndarray[np.float32_t, ndim=1] ve = v.np
    s[0] = ve[0]
    s[1] = ve[1]
    s[2] = ve[2]

cpdef int cVector_equals(np.ndarray[np.float32_t, ndim=1] self, np.ndarray[np.float32_t, ndim=1] v):
    return self[0] == v[0] and self[1] == v[1] and self[2] == v[2]

cpdef cVector3_less_than(np.ndarray[np.float32_t, ndim=1] self, np.ndarray[np.float32_t, ndim=1] v):
    return self[0] < v[0] or self[1] < v[1] or self[2] < v[2]

cpdef cVector3_greater_than(np.ndarray[np.float32_t, ndim=1] self, np.ndarray[np.float32_t, ndim=1] v):
    return self[0] > v[0] or self[1] > v[1] or self[2] > v[2]
