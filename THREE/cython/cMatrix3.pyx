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


cpdef void cMatrix3_getInverse(np.ndarray[np.float32_t, ndim=1] te ,
                        np.ndarray[np.float32_t, ndim=1] me ):
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

cpdef cMatrix3_getNormalMatrix(self, matrix4):
    cdef np.ndarray[np.float32_t, ndim=1] npself = self.elements
    cdef np.ndarray[np.float32_t, ndim=1] npmatrix4 = matrix4.elements
    cdef np.float32_t tmp

    # setFromMatrix4(matrix4)
    npself[0] = npmatrix4[0];    npself[3] = npmatrix4[4];    npself[6] = npmatrix4[8]
    npself[1] = npmatrix4[1];    npself[4] = npmatrix4[5];    npself[7] = npmatrix4[9]
    npself[2] = npmatrix4[2];    npself[5] = npmatrix4[6];    npself[8] = npmatrix4[10]

    cMatrix3_getInverse(npself, npself)

    # transpose
    tmp = npself[1]; npself[1] = npself[3]; npself[3] = tmp
    tmp = npself[2]; npself[2] = npself[6]; npself[6] = tmp
    tmp = npself[5]; npself[5] = npself[7]; npself[7] = tmp
