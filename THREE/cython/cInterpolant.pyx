#cython: cdivision=True
#cython: boundscheck=False
#cython: wraparound=False

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

import THREE.math.Interpolant
from THREE.cython.cQuaternion import cQuaternion_slerpFlat


def cInterpolant_evaluate(self, float t ):
    cdef np.ndarray[float, ndim=1, mode="c"] nd_pp = self.parameterPositions
    cdef float *pp = <float *>&nd_pp[0]

    cdef int len_pp = len(nd_pp)
    cdef int i1 = self._cachedIndex
    cdef int mid
    cdef int right
    cdef int giveUpAt

    cdef float t1
    cdef float t0
    cdef float t1global

    cdef int t1_defined
    cdef int t0_defined

    if i1 < len_pp:
        t1 = pp[   i1   ]
        t1_defined = True
    else:
        t1_defined = False

    if i1 > 0:
        t0 = pp[ i1 - 1 ]
        t0_defined = True
    else:
        t0_defined = False

    cdef int status = 0  # _none

    if not t1_defined or t >= t1:
        giveUpAt = i1 + 2
        while True:
            if not t1_defined:
                if t < t0:
                    break

                # after end
                i1 = len_pp
                self._cachedIndex = i1
                return self.afterEnd_(i1 - 1, t, t0)

            if i1 == giveUpAt:
                break  # // self loop

            t0 = t1
            t0_defined = t1_defined

            i1 += 1
            if i1 >= len_pp:
                continue

            t1 = pp[i1]
            t1_defined = True

            if t < t1:
                # we have arrived at the sought interval
                status = 2  # _seek
                break

        # prepare binary search on the right side of the index
        if not status:   # _none:
            right = len_pp
            status = 3  # _linear_scan

    if not status and (not t0_defined or t < t0):
        # looping?
        t1global = pp[1]

        if t < t1global:
            i1 = 2  # + 1, using the scan for the details
            t0 = t1global
            t0_defined = True

        # linear reverse scan
        giveUpAt = i1 - 2
        while True:
            if not t0_defined:
                # before start
                self._cachedIndex = 0
                return self.beforeStart_(0, t, t1)

            if i1 == giveUpAt:
                break  # self loop

            t1 = t0
            t1_defined = t0_defined

            i1 -= 1
            t0 = pp[i1 - 1]
            t0_defined = True

            if t >= t0:
                # we have arrived at the sought interval
                status = 2  # _seek
                break

        # prepare binary search on the left side of the index
        if not status:
            right = i1
            i1 = 0
            status = 3   # _linear_scan

    # the interval is valid
    if not status:
        status = 4  # _validate_interval

    if status == 3:  # _linear_scan:
        status = 0  # _none

    # binary search
    if not status:  # _none:
        while i1 < right:
            mid = (i1 + right) >> 1

            if t < pp[mid]:
                right = mid
            else:
                i1 = mid + 1

        if i1 < len_pp:
            t1 = pp[i1]
            t1_defined = True
        else:
            t1_defined = False

        if 0 < i1 < len_pp:
            t0 = pp[i1 - 1]
            t0_defined = True
        else:
            t0_defined = False

        # check boundary cases, again
        if not t0_defined:
            self._cachedIndex = 0
            return self.beforeStart_(0, t, t1)

        if not t1_defined:
            i1 = len_pp
            self._cachedIndex = i1
            return self.afterEnd_(i1 - 1, t0, t)

    if not status or status == 2:
        self._cachedIndex = i1
        self.intervalChanged_(i1, t0, t1)

    return self.interpolate_( i1, t0, t, t1 )


"""
"""
def cLinearInterpolant_interpolate_(np.ndarray[float, ndim=1] result not None,
                                    np.ndarray[float, ndim=1] values not None,
                                    int stride,
                                    int i1,
                                    float t0,
                                    float t,
                                    float t1 ):
    cdef int offset1 = i1 * stride
    cdef int offset0 = offset1 - stride

    cdef float weight1 = ( t - t0 ) / ( t1 - t0 )
    cdef float weight0 = 1 - weight1
    cdef float a
    cdef float b
    cdef int i

    for i in range(stride):
        a = values[ offset0 + i ]
        b = values[ offset1 + i ]
        result[ i ] = a * weight0 + b * weight1

    return result

"""
"""
def cQuaternionLinearInterpolant_interpolate_(object self, int i1, double t0, double t, double t1 ):
    cdef np.ndarray[float, ndim=1] result = self.resultBuffer
    cdef np.ndarray[float, ndim=1] values = self.sampleValues
    cdef int stride = self.valueSize

    cdef int offset = i1 * stride

    cdef float alpha = ( t - t0 ) / ( t1 - t0 )

    for offset in range(i1 * stride, offset + stride, 4 ):
        cQuaternion_slerpFlat(result, 0, values, offset - stride, values, offset, alpha )

    return result
