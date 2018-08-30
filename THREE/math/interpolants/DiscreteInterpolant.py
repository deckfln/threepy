"""
 *
 * Interpolant that evaluates to the sample value at the position preceeding
 * the parameter.
 *
 * @author tschw
"""
from THREE.math.Interpolant import *


class DiscreteInterpolant(Interpolant):
    def __init__(self, parameterPositions, sampleValues, sampleSize, resultBuffer ):
        super().__init__(parameterPositions, sampleValues, sampleSize, resultBuffer )

    def interpolate_(self, i1, t0, t, t1 ):
        return self.copySampleValue_( i1 - 1 )
