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


cdef _getInverse(float *t, float *m):
    cdef np.float32_t n11 = m[ 0 ]
    cdef np.float32_t n21 = m[ 1 ]
    cdef np.float32_t n31 = m[ 2 ]
    cdef np.float32_t n12 = m[ 3 ]
    cdef np.float32_t n22 = m[ 4 ]
    cdef np.float32_t n32 = m[ 5 ]
    cdef np.float32_t n13 = m[ 6 ]
    cdef np.float32_t n23 = m[ 7 ]
    cdef np.float32_t n33 = m[ 8 ]

    cdef np.float32_t t11 = n33 * n22 - n32 * n23
    cdef np.float32_t t12 = n32 * n13 - n33 * n12
    cdef np.float32_t t13 = n23 * n12 - n22 * n13

    cdef np.float32_t det = n11 * t11 + n21 * t12 + n31 * t13
    cdef np.float32_t detInv

    if det == 0:
        # raise RuntimeWarning("THREE.Matrix3: .getInverse() can't invert matrix, determinant is 0")
        t[0] = 1
        t[1] = 0
        t[2] = 0
        t[3] = 0
        t[4] = 1
        t[5] = 0
        t[6] = 0
        t[7] = 0
        t[8] = 1
    else:
        detInv = 1 / det
        t[ 0 ] = t11 * detInv
        t[ 1 ] = ( n31 * n23 - n33 * n21 ) * detInv
        t[ 2 ] = ( n32 * n21 - n31 * n22 ) * detInv

        t[ 3 ] = t12 * detInv
        t[ 4 ] = ( n33 * n11 - n31 * n13 ) * detInv
        t[ 5 ] = ( n31 * n12 - n32 * n11 ) * detInv

        t[ 6 ] = t13 * detInv
        t[ 7 ] = ( n21 * n13 - n23 * n11 ) * detInv
        t[ 8 ] = ( n22 * n11 - n21 * n12 ) * detInv

cpdef void cMatrix3_getInverse(self, target):
    cdef np.ndarray[np.float32_t, ndim=1] te = self.elements
    cdef np.ndarray[np.float32_t, ndim=1] me = target.elements

    cdef float *t = <float *>&te[0]
    cdef float *m = <float *>&me[0]

    _getInverse(t, m)

cpdef cMatrix3_getNormalMatrix(self, matrix4):
    cdef np.ndarray[np.float32_t, ndim=1] npself = self.elements
    cdef np.ndarray[np.float32_t, ndim=1] npmatrix4 = matrix4.elements

    cdef float *s = <float *>&npself[0]
    cdef float *m = <float *>&npmatrix4[0]
    cdef np.float32_t tmp

    # setFromMatrix4(matrix4)
    s[0] = m[0];    s[3] = m[4];    s[6] = m[8]
    s[1] = m[1];    s[4] = m[5];    s[7] = m[9]
    s[2] = m[2];    s[5] = m[6];    s[8] = m[10]

    _getInverse(s, s)

    # transpose
    tmp = s[1]; s[1] = s[3]; s[3] = tmp
    tmp = s[2]; s[2] = s[6]; s[6] = tmp
    tmp = s[5]; s[5] = s[7]; s[7] = tmp
