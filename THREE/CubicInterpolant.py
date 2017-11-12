"""
 * Fast and simple cubic spline interpolant.
 *
 * It was derived from a Hermitian construction setting the first derivative
 * at each sample position to the linear slope between neighboring positions
 * over their parameter interval.
 *
 * @author tschw
"""
from THREE.Interpolant import *
from THREE.Constants import *


class CubicInterpolant(Interpolant):
    DefaultSettings_ = {
        'endingStart':     ZeroCurvatureEnding,
        'endingEnd':    ZeroCurvatureEnding
    }

    def __init__(self, parameterPositions, sampleValues, sampleSize, resultBuffer ):
        super().__init__(parameterPositions, sampleValues, sampleSize, resultBuffer )

        self._weightPrev = -0
        self._offsetPrev = -0
        self._weightNext = -0
        self._offsetNext = -0

    def intervalChanged_(self, i1, t0, t1 ):
        pp = self.parameterPositions
        iPrev = i1 - 2
        iNext = i1 + 1

        tPrev = pp[ iPrev ]
        tNext = pp[ iNext ]

        if tPrev is None:
            es = self.getSettings_().endingStart
            if es == ZeroSlopeEnding:
                # f'(t0) = 0
                iPrev = i1
                tPrev = 2 * t0 - t1

            elif es == WrapAroundEnding:
                # use the other end of the curve
                iPrev = len(pp) - 2
                tPrev = t0 + pp[ iPrev ] - pp[ iPrev + 1 ]

            else:     #ZeroCurvatureEnding
                # f''(t0) = 0 a.k.a. Natural Spline
                iPrev = i1
                tPrev = t1

        if tNext is None:
            ee = self.getSettings_().endingEnd
            if ee == ZeroSlopeEnding:
                # f'(tN) = 0
                iNext = i1
                tNext = 2 * t1 - t0

            elif ee == WrapAroundEnding:
                # use the other end of the curve
                iNext = 1
                tNext = t1 + pp[ 1 ] - pp[ 0 ]

            else: # ZeroCurvatureEnding
                # f''(tN) = 0, a.k.a. Natural Spline
                iNext = i1 - 1
                tNext = t0

        halfDt = ( t1 - t0 ) * 0.5
        stride = self.valueSize

        self._weightPrev = halfDt / ( t0 - tPrev )
        self._weightNext = halfDt / ( tNext - t1 )
        self._offsetPrev = iPrev * stride
        self._offsetNext = iNext * stride

    def interpolate_(self, i1, t0, t, t1 ):
        result = self.resultBuffer
        values = self.sampleValues
        stride = self.valueSize

        o1 = i1 * stride
        o0 = o1 - stride,
        oP = self._offsetPrev
        oN = self._offsetNext
        wP = self._weightPrev
        wN = self._weightNext

        p = ( t - t0 ) / ( t1 - t0 )
        pp = p * p
        ppp = pp * p

        # evaluate polynomials

        sP =     - wP   * ppp   +         2 * wP    * pp    -          wP   * p
        s0 = ( 1 + wP ) * ppp   + (-1.5 - 2 * wP )  * pp    + ( -0.5 + wP ) * p     + 1
        s1 = (-1 - wN ) * ppp   + ( 1.5 +   wN   )  * pp    +    0.5        * p
        sN =       wN   * ppp   -           wN      * pp

        # combine data linearly

        for i in range(stride):
            result[ i ] = sP * values[ oP + i ] + \
                    s0 * values[ o0 + i ] + \
                    s1 * values[ o1 + i ] + \
                    sN * values[ oN + i ]

        return result
