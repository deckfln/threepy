"""
 * @author tschw
"""
from THREE.Interpolant import *
from THREE.cython.cthree import *


class LinearInterpolant(Interpolant):
    def __init__(self, parameterPositions, sampleValues, sampleSize, resultBuffer ):
        super().__init__(parameterPositions, sampleValues, sampleSize, resultBuffer )

    def interpolate_(self, i1, t0, t, t1 ):
        return cinterpolate_(self.resultBuffer, self.sampleValues, self.valueSize, i1, t0, t, t1)

    def _interpolate_(self, i1, t0, t, t1 ):
        result = self.resultBuffer
        values = self.sampleValues
        stride = self.valueSize

        offset1 = i1 * stride
        offset0 = offset1 - stride

        weight1 = ( t - t0 ) / ( t1 - t0 )
        weight0 = 1 - weight1

        for i in range(stride):
            result[ i ] = values[ offset0 + i ] * weight0 + values[ offset1 + i ] * weight1

        return result
