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

cpdef cMatrix3_getNormalMatrix(np.ndarray[np.float32_t, ndim=1] self, np.ndarray[np.float32_t, ndim=1] matrix4):
    cdef np.float32_t tmp

    # setFromMatrix4(matrix4)
    self[0] = matrix4[0];    self[3] = matrix4[4];    self[6] = matrix4[8]
    self[1] = matrix4[1];    self[4] = matrix4[5];    self[7] = matrix4[9]
    self[2] = matrix4[2];    self[5] = matrix4[6];    self[8] = matrix4[10]

    cMatrix3_getInverse(self, self)

    # transpose
    tmp = self[1]; self[1] = self[3]; self[3] = tmp
    tmp = self[2]; self[2] = self[6]; self[6] = tmp
    tmp = self[5]; self[5] = self[7]; self[7] = tmp
