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

from THREE.cython.cthree import cPlane_distanceToPoint

cpdef cFrustum_intersectsSphere(list planes, sphere ):
    """
    Optimization based on http://blog.bwhiting.co.uk/?p=355
    :param sphere:
    :return:
    """
    cdef float negRadius = - sphere.radius
    cdef int p
    cdef float distance

    cdef int cache = sphere.cache
    cdef np.ndarray[np.float32_t, ndim=1] center = sphere.center.np
    cdef np.ndarray[np.float32_t, ndim=1] normal
    cdef np.float32_t constant

    if cache >= 0:
        plane = planes[cache]
        normal = plane.normal.np
        constant = plane.constant
        distance = cPlane_distanceToPoint(normal, center, constant)
        if distance < negRadius:
            return False

    for p in range(6):
        if p == cache:
            continue

        plane = planes[p]
        distance = cPlane_distanceToPoint(normal, center, constant)

        if distance < negRadius:
            sphere.cache = p
            return False

    sphere.cache = -1
    return True
