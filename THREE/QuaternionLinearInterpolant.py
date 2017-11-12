"""
 * Spherical linear unit quaternion interpolant.
 *
 * @author tschw
"""
from THREE.Interpolant import *


class QuaternionLinearInterpolant(Interpolant):
    def __init__(self, parameterPositions, sampleValues, sampleSize, resultBuffer ):
        super().__init__(parameterPositions, sampleValues, sampleSize, resultBuffer )

    def interpolate_(self, i1, t0, t, t1 ):
        result = this.resultBuffer
        values = this.sampleValues
        stride = this.valueSize

        offset = i1 * stride

        alpha = ( t - t0 ) / ( t1 - t0 )

        for offset in range(i1 * stride, offset + stride, 4 ):
            Quaternion.slerpFlat( result, 0,values, offset - stride, values, offset, alpha )

        return result
