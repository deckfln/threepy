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

cpdef void cVector3_lerp(np.ndarray[np.float32_t, ndim=1] self, np.ndarray[np.float32_t, ndim=1] v, float alpha):
    self[0] += ( v[0] - self[0] ) * alpha
    self[1] += ( v[1] - self[1] ) * alpha
    self[2] += ( v[2] - self[2] ) * alpha

cdef cVector3__copy(np.ndarray[np.float32_t, ndim=1] self, np.ndarray[np.float32_t, ndim=1] v):
    self[0] = v[0]
    self[1] = v[1]
    self[2] = v[2]

cpdef void cVector3_copy(self, v):
    cdef np.ndarray[np.float32_t, ndim=1] s = self.np
    cdef np.ndarray[np.float32_t, ndim=1] ve = v.np
    s[0] = ve[0]
    s[1] = ve[1]
    s[2] = ve[2]

cpdef int cVector_equals(self, v):
    cdef np.ndarray[np.float32_t, ndim=1] snp = self.np
    cdef np.ndarray[np.float32_t, ndim=1] vnp = v.np
    return snp[0] == vnp[0] and snp[1] == vnp[1] and snp[2] == vnp[2]

cpdef cVector3_less_than(np.ndarray[np.float32_t, ndim=1] self, np.ndarray[np.float32_t, ndim=1] v):
    return self[0] < v[0] or self[1] < v[1] or self[2] < v[2]

cpdef cVector3_greater_than(np.ndarray[np.float32_t, ndim=1] self, np.ndarray[np.float32_t, ndim=1] v):
    return self[0] > v[0] or self[1] > v[1] or self[2] > v[2]
