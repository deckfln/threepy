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
from libc.stdlib cimport malloc, free

"""
cdef extern from "frustum.c":
    void sse_culling_spheres(float *sphere_data, int num_objects, int *culling_res, float *frustum_planes)

cpdef cFrustum_intersectsObjects(self, objects, _sphere, visible):
    cdef np.float32_t *spheres = <np.float32_t *>malloc(len(objects) * 4 * sizeof(np.float32))
    cdef int *culling_res = <int *>malloc(len(objects) * sizeof(int))
    cdef int num_objects
    cdef np.ndarray[np.float32_t, ndim=1] center = _sphere.center.np
    cdef np.ndarray[np.float32_t, ndim=1] frustum_planes = self._planes
    cdef int i

    for object in objects:
        geometry = object.geometry

        # only compute the intersection if
        #   the camera moved
        #   or the object moved
        #   or the object is not yet in the cache
        if self.updated or object.matrixWorld.updated or object.id not in self._cache:
            if geometry.boundingSphere is None:
                geometry.computeBoundingSphere()

            _sphere.copy( geometry.boundingSphere )
            _sphere.applyMatrix4( object.matrixWorld )

            spheres[p] = center[0]
            spheres[p + 1] = center[1]
            spheres[p + 2] = center[2]
            spheres[p + 3] = _sphere.constant

            p += 4
            num_objects += 1

    sse_culling_spheres(spheres, num_objects, culling_res, &frustum_planes[0])

    for i in range(num_objects):
        if culling_res[i]:
            visible.append(objects[i])

    free(spheres)
    free(culling_res)
"""

cpdef cFrustum_intersectsSphere(self, sphere):
    """
    Optimization based on http://blog.bwhiting.co.uk/?p=355
    :param sphere:
    :return:
    """
    cdef np.float32_t negRadius = - sphere.radius
    cdef int p
    cdef int pi
    cdef np.float32_t distance

    cdef int cache = sphere.cache
    cdef np.ndarray[np.float32_t, ndim=1] point = sphere.center.np
    cdef np.ndarray[np.float32_t, ndim=1] planes = self._planes

    if cache >= 0:
        pi = cache * 4
        distance = planes[pi] * point[0] + planes[pi + 1] * point[1] + planes[pi + 2] * point[2] + planes[pi + 3]

        if distance < negRadius:
            return False

    for p in range(6):
        if p == cache:
            continue

        pi = p * 4
        distance = planes[pi] * point[0] + planes[pi + 1] * point[1] + planes[pi + 2] * point[2] + planes[pi + 3]

        if distance < negRadius:
            sphere.cache = p
            return False

    sphere.cache = -1
    return True
