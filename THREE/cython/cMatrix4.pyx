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
cdef extern from "matrix4.c":
    void M4x4_SSE(float *A, float *B, float *C)
    void M4x4(float *A, float *B, float *C)


"""
Matrix4
"""
cpdef c_Matrix4_makeRotationFromQuaternion(np.ndarray[np.float32_t, ndim=1] te , float x, float y, float z, float w):
    cdef np.float32_t x2 = x + x
    cdef np.float32_t y2 = y + y
    cdef np.float32_t z2 = z + z
    cdef np.float32_t xx = x * x2
    cdef np.float32_t xy = x * y2
    cdef np.float32_t xz = x * z2
    cdef np.float32_t yy = y * y2
    cdef np.float32_t yz = y * z2
    cdef np.float32_t zz = z * z2
    cdef np.float32_t wx = w * x2
    cdef np.float32_t wy = w * y2
    cdef np.float32_t wz = w * z2

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


cpdef cMatrix4_sse_multiplyMatrices(object self, object a, object b):
    cdef np.ndarray[np.float32_t, ndim=1] te = self.elements
    cdef np.ndarray[np.float32_t, ndim=1] ae = a.elements
    cdef np.ndarray[np.float32_t, ndim=1] be = b.elements
    cdef float *af = &ae[0]
    cdef float *bf = &be[0]
    cdef float *cf = &te[0]

    M4x4(af, bf, cf)


cpdef cMatrix4_multiplyMatrices(self, a, b):
    cdef np.ndarray[np.float32_t, ndim=1] te = self.elements
    cdef np.ndarray[np.float32_t, ndim=1] ae = a.elements
    cdef np.ndarray[np.float32_t, ndim=1] be = b.elements

    cdef np.float32_t a11
    cdef np.float32_t a12
    cdef np.float32_t a13
    cdef np.float32_t a14
    cdef np.float32_t a21
    cdef np.float32_t a22
    cdef np.float32_t a23
    cdef np.float32_t a24
    cdef np.float32_t a31
    cdef np.float32_t a32
    cdef np.float32_t a33
    cdef np.float32_t a34
    cdef np.float32_t a41
    cdef np.float32_t a42
    cdef np.float32_t a43
    cdef np.float32_t a44

    cdef np.float32_t b11
    cdef np.float32_t b12
    cdef np.float32_t b13
    cdef np.float32_t b14
    cdef np.float32_t b21
    cdef np.float32_t b22
    cdef np.float32_t b23
    cdef np.float32_t b24
    cdef np.float32_t b31
    cdef np.float32_t b32
    cdef np.float32_t b33
    cdef np.float32_t b34
    cdef np.float32_t b41
    cdef np.float32_t b42
    cdef np.float32_t b43
    cdef np.float32_t b44

    a11 = ae[0]
    a12 = ae[4]
    a13 = ae[8]
    a14 = ae[12]
    b11 = be[0]
    b21 = be[1]
    b31 = be[2]
    b41 = be[3]
    te[0] = a11 * b11 + a12 * b21 + a13 * b31 + a14 * b41

    b12 = be[4]
    b22 = be[5]
    b32 = be[6]
    b42 = be[7]
    te[4] = a11 * b12 + a12 * b22 + a13 * b32 + a14 * b42

    b13 = be[8]
    b23 = be[9]
    b33 = be[10]
    b43 = be[11]
    te[8] = a11 * b13 + a12 * b23 + a13 * b33 + a14 * b43

    b14 = be[12]
    b24 = be[13]
    b34 = be[14]
    b44 = be[15]
    te[12] = a11 * b14 + a12 * b24 + a13 * b34 + a14 * b44

    a21 = ae[1]
    a22 = ae[5]
    a23 = ae[9]
    a24 = ae[13]
    te[1] = a21 * b11 + a22 * b21 + a23 * b31 + a24 * b41
    te[5] = a21 * b12 + a22 * b22 + a23 * b32 + a24 * b42
    te[9] = a21 * b13 + a22 * b23 + a23 * b33 + a24 * b43
    te[13] = a21 * b14 + a22 * b24 + a23 * b34 + a24 * b44

    a31 = ae[2]
    a32 = ae[6]
    a33 = ae[10]
    a34 = ae[14]
    te[2] = a31 * b11 + a32 * b21 + a33 * b31 + a34 * b41
    te[6] = a31 * b12 + a32 * b22 + a33 * b32 + a34 * b42
    te[10] = a31 * b13 + a32 * b23 + a33 * b33 + a34 * b43
    te[14] = a31 * b14 + a32 * b24 + a33 * b34 + a34 * b44

    a41 = ae[3]
    a42 = ae[7]
    a43 = ae[11]
    a44 = ae[15]
    te[3] = a41 * b11 + a42 * b21 + a43 * b31 + a44 * b41
    te[7] = a41 * b12 + a42 * b22 + a43 * b32 + a44 * b42
    te[11] = a41 * b13 + a42 * b23 + a43 * b33 + a44 * b43
    te[15] = a41 * b14 + a42 * b24 + a43 * b34 + a44 * b44


cpdef cMatrix4_scale(np.ndarray[np.float32_t, ndim=1] te , np.ndarray[np.float32_t, ndim=1] v ):
    te[0] *= v[0]
    te[4] *= v[1]
    te[8] *= v[2]
    te[1] *= v[0]
    te[5] *= v[1]
    te[9] *= v[2]
    te[2] *= v[0]
    te[6] *= v[1]
    te[10] *= v[2]
    te[3] *= v[0]
    te[7] *= v[1]
    te[11] *= v[2]


cpdef cMatrix4_setPosition(np.ndarray[np.float32_t, ndim=1] te , np.ndarray[np.float32_t, ndim=1] v ):
    te[12] = v[0]
    te[13] = v[1]
    te[14] = v[2]


cpdef cMatrix4_compose(np.ndarray[np.float32_t, ndim=1] te, np.ndarray[np.float32_t, ndim=1] position ,
                        np.ndarray[np.float32_t, ndim=1] scale ,
                        double x,
                        double y,
                        double z,
                        double w):
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

    cdef double xs = scale[0]
    cdef double ys = scale[1]
    cdef double zs = scale[2]

    te[0] = (1 - (yy + zz)) * xs
    te[4] = (xy - wz) * ys
    te[8] = (xz + wy) * zs

    te[1] = (xy + wz) * xs
    te[5] = (1 - (xx + zz)) * ys
    te[9] = (yz - wx) * ys

    te[2] = (xz - wy) * xs
    te[6] = (yz + wx) * ys
    te[10] = (1 - (xx + yy)) * zs

    # // last column
    te[3] = 0
    te[7] = 0
    te[11] = 0

    # // bottom row
    te[15] = 1

    te[12] = position[0]
    te[13] = position[1]
    te[14] = position[2]


cpdef cMatrix4_getMaxScaleOnAxis(np.ndarray[np.float32_t, ndim=1] te ):
    cdef float scaleXSq = te[0] * te[0] + te[1] * te[1] + te[2] * te[2]
    cdef float scaleYSq = te[4] * te[4] + te[5] * te[5] + te[6] * te[6]
    cdef float scaleZSq = te[8] * te[8] + te[9] * te[9] + te[10] * te[10]

    return sqrt(max(scaleXSq, scaleYSq, scaleZSq))
