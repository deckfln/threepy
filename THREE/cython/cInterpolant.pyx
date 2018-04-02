"""
    /**
     * @author mrdoob / http://mrdoob.com/
     * @author kile / http://kile.stravaganza.org/
     * @author philogb / http://blog.thejit.org/
     * @author mikael emtinger / http://gomo.se/
     * @author egraether / http://egraether.com/
     * @author WestLangley / http://github.com/WestLangley
     */
"""

cimport cython

import numpy as np
cimport numpy as np
from libc.math cimport sqrt, atan2, sin

import THREE.Interpolant

_none = 0
_forward_scan = 1
_seek = 2
_linear_scan = 3
_validate_interval = 4

def cInterpolant_evaluate(self, float t ):
    cdef np.ndarray[float, ndim=1] pp = self.parameterPositions
    cdef int len_pp = len(pp)
    cdef int i1 = self._cachedIndex
    cdef int mid

    t1 = pp[   i1   ] if i1 < len_pp else None
    t0 = pp[ i1 - 1 ] if i1 > 0 else None

    right = None

    cdef int status = _none
    if t1 is None or t >= t1:
        giveUpAt = i1 + 2
        while True:
            if t1 is None:
                if t < t0:
                    break

                # after end
                i1 = len_pp
                self._cachedIndex = i1
                return self.afterEnd_(i1 - 1, t, t0)

            if i1 == giveUpAt:
                break  # // self loop

            t0 = t1
            i1 += 1
            if i1 >= len_pp:
                continue

            t1 = pp[i1]

            if t < t1:
                # we have arrived at the sought interval
                status = _seek
                break

        # prepare binary search on the right side of the index
        if status == _none:
            right = len_pp
            status = _linear_scan

    if status == _none and (t0 is None or t < t0):
        # looping?
        t1global = pp[1]

        if t < t1global:
            i1 = 2  # + 1, using the scan for the details
            t0 = t1global

        # linear reverse scan
        giveUpAt = i1 - 2
        while True:
            if t0 is None:
                # before start
                self._cachedIndex = 0
                return self.beforeStart_(0, t, t1)

            if i1 == giveUpAt:
                break  # self loop

            t1 = t0
            i1 -= 1
            t0 = pp[i1 - 1]

            if t >= t0:
                # we have arrived at the sought interval
                status = _seek
                break

        # prepare binary search on the left side of the index
        if status == _none:
            right = i1
            i1 = 0
            status = _linear_scan

    # the interval is valid
    if status == _none:
        status = _validate_interval

    if status == _linear_scan:
        status = _none

    # binary search
    if status == _none:
        while i1 < right:
            mid = (i1 + right) >> 1

            if t < pp[mid]:
                right = mid
            else:
                i1 = mid + 1

        t1 = pp[i1] if i1 < len_pp else None
        t0 = pp[i1 - 1] if 0 < i1 < len_pp else None

        # check boundary cases, again
        if t0 is None:
            self._cachedIndex = 0
            return self.beforeStart_(0, t, t1)

        if t1 is None:
            i1 = len_pp
            self._cachedIndex = i1
            return self.afterEnd_(i1 - 1, t0, t)

    if status == _none or status == _seek:
        self._cachedIndex = i1
        self.intervalChanged_(i1, t0, t1)

    return self.interpolate_( i1, t0, t, t1 )
