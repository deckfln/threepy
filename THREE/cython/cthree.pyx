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


"""
Matrix4
"""
cpdef c_Matrix4_makeRotationFromQuaternion(np.ndarray[float, ndim=1] te , double x, double y, double z, double w):
    cdef float x2 = x + x
    cdef float y2 = y + y
    cdef float z2 = z + z
    cdef float xx = x * x2
    cdef float xy = x * y2
    cdef float xz = x * z2
    cdef float yy = y * y2
    cdef float yz = y * z2
    cdef float zz = z * z2
    cdef float wx = w * x2
    cdef float wy = w * y2
    cdef float wz = w * z2

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


cpdef cMatrix4_multiplyMatrices(np.ndarray[np.float32_t, ndim=1] te , np.ndarray[np.float32_t, ndim=1] ae , np.ndarray[np.float32_t, ndim=1] be ):
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

cpdef cMatrix4_scale(np.ndarray[float, ndim=1] te , np.ndarray[float, ndim=1] v ):
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

cpdef cMatrix4_setPosition(np.ndarray[float, ndim=1] te , np.ndarray[float, ndim=1] v ):
    te[12] = v[0]
    te[13] = v[1]
    te[14] = v[2]

cpdef cMatrix4_compose(np.ndarray[float, ndim=1] te, np.ndarray[float, ndim=1] position ,
                        np.ndarray[float, ndim=1] scale ,
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

cpdef cMatrix4_getMaxScaleOnAxis(np.ndarray[float, ndim=1] te ):
    cdef float scaleXSq = te[0] * te[0] + te[1] * te[1] + te[2] * te[2]
    cdef float scaleYSq = te[4] * te[4] + te[5] * te[5] + te[6] * te[6]
    cdef float scaleZSq = te[8] * te[8] + te[9] * te[9] + te[10] * te[10]

    return sqrt(max(scaleXSq, scaleYSq, scaleZSq))

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
Vector3
"""
cpdef void cVector3_applyMatrix4(np.ndarray[float, ndim=1] vector3 ,
                                np.ndarray[float, ndim=1] matrix4 ):
    cdef float x = vector3[0]
    cdef float y = vector3[1]
    cdef float z = vector3[2]

    cdef float w = 1 / ( matrix4[ 3 ] * x + matrix4[ 7 ] * y + matrix4[ 11 ] * z + matrix4[ 15 ] );

    vector3[0] = ( matrix4[ 0 ] * x + matrix4[ 4 ] * y + matrix4[ 8 ]  * z + matrix4[ 12 ] ) * w;
    vector3[1] = ( matrix4[ 1 ] * x + matrix4[ 5 ] * y + matrix4[ 9 ]  * z + matrix4[ 13 ] ) * w;
    vector3[2] = ( matrix4[ 2 ] * x + matrix4[ 6 ] * y + matrix4[ 10 ] * z + matrix4[ 14 ] ) * w;

cpdef void cVector3_applyMatrix3(np.ndarray[float, ndim=1] this ,
                            np.ndarray[float, ndim=1] e ):
    cdef float x = this[0]
    cdef float y = this[1]
    cdef float z = this[2]

    this[0] = e[ 0 ] * x + e[ 3 ] * y + e[ 6 ] * z
    this[1] = e[ 1 ] * x + e[ 4 ] * y + e[ 7 ] * z
    this[2] = e[ 2 ] * x + e[ 5 ] * y + e[ 8 ] * z

cpdef void cVector3_getInverse(np.ndarray[np.float32_t, ndim=1] te ,
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

    cVector3_getInverse(self, self)

    # transpose
    tmp = self[1]; self[1] = self[3]; self[3] = tmp
    tmp = self[2]; self[2] = self[6]; self[6] = tmp
    tmp = self[5]; self[5] = self[7]; self[7] = tmp

cpdef void cVector3_lerp(np.ndarray[float, ndim=1] self ,
                np.ndarray[float, ndim=1] v ,
                float alpha ):
    self[0] += ( v[0] - self[0] ) * alpha
    self[1] += ( v[1] - self[1] ) * alpha
    self[2] += ( v[2] - self[2] ) * alpha

cpdef void cVector3_copy(np.ndarray[float, ndim=1] self ,
                np.ndarray[float, ndim=1] v ):
    cdef void *source = <void *>&v[0]
    cdef void *dest = <void *>&self[0]

    memcpy(dest, source, 3*sizeof(float))

cpdef int cVector_equals(np.ndarray[float, ndim=1] self ,
                np.ndarray[float, ndim=1] v ):
    cdef void *dest = <void *>&self[0]
    cdef void *source = <void *>&v[0]

    return memcmp(source, dest, 3*sizeof(float))

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
cpdef cPlane_distanceToPoint(np.ndarray[float, ndim=1] normal ,
                            np.ndarray[float, ndim=1] point ,
                            double constant ):
    return normal[0] * point[0] + normal[1] * point[1] + normal[2] * point[2] + constant

"""
Sphere
"""
cpdef cSphere_applyMatrix4(object self, object matrix ):
    cdef np.ndarray[float, ndim=1] center = self.center.np
    cdef np.ndarray[float, ndim=1] matrix4 = matrix.elements
    cdef double radius = self.radius

    cVector3_applyMatrix4(center, matrix4)
    radius = radius * cMatrix4_getMaxScaleOnAxis(matrix4)

    self.radius = radius
    return self

cpdef cSphere_intersectsSphere(list planes, sphere ):
    """
    Optimization based on http://blog.bwhiting.co.uk/?p=355
    :param sphere:
    :return:
    """
    cdef object center = sphere.center
    cdef double negRadius = - sphere.radius
    cdef int p
    cdef double distance

    if sphere.cache >= 0:
        plane = planes[sphere.cache]
        distance = cPlane_distanceToPoint(plane.normal.np, sphere.center.np, plane.constant)
        if distance < negRadius:
            return False

    for p in range(6):
        if p == sphere.cache:
            continue

        plane = planes[p]
        distance = cPlane_distanceToPoint(plane.normal.np, sphere.center.np, plane.constant)

        if distance < negRadius:
            sphere.cache = p
            return False

    sphere.cache = -1
    return True

cpdef cUpdateValueArrayElement(long long buffer, int offset, long long element, long long element_size, long long data, long long size):
    """
    Update a single uniform in an array of uniforms
    :param self:
    :param value:
    :param buffer:
    :param element:
    :return:
    """
    memcpy(<void *>(buffer + offset + element * element_size), <void *>data, size)

cpdef cUpdateValueMat3ArrayElement(long long buffer, int offset, long long element, long long element_size, long long data, long long size):
    """
    Mat3 are stored as 3 rows of vec4 in STD140
    """
    cdef long long start = buffer + offset + element * element_size

    memcpy(<void *>start, <void *>data, 12)
    memcpy(<void *>(start + 16), <void *>(data + 12), 12)
    memcpy(<void *>(start + 32), <void *>(data + 24), 12)
