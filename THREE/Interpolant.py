"""
 * Abstract base class of interpolants over parametric samples.
 *
 * The parameter domain is one dimensional, typically the time or a path
 * along a curve defined by the data.
 *
 * The sample values can have any dimensionality and derived classes may
 * apply special interpretations to the data.
 *
 * This class provides the interval seek in a Template Method, deferring
 * the actual interpolation to derived classes.
 *
 * Time complexity is O(1) for linear access crossing at most two points
 * and O(log N) for random access, where N is the number of positions.
 *
 * References:
 *
 *         http:#www.oodesign.com/template-method-pattern.html
 *
 * @author tschw
"""


class Interpolant:
    settings = None # optional, subclass-specific settings structure
    # Note: The indirection allows central control of many interpolants.

    DefaultSettings_ = {}

    def __init__(self, parameterPositions, sampleValues, sampleSize, resultBuffer ):
        self.parameterPositions = parameterPositions
        self._cachedIndex = 0

        self.resultBuffer = resultBuffer if resultBuffer is None else sampleValues.constructor( sampleSize )
        self.sampleValues = sampleValues
        self.valueSize = sampleSize
        #( 0, t, t0 ), returns self.resultBuffer
        self.beforeStart_ = self.copySampleValue_

        #( N-1, tN-1, t ), returns self.resultBuffer
        self.afterEnd_ = self.copySampleValue_

    def evaluate(self, t ):
        pp = self.parameterPositions
        len_pp = len(pp)
        i1 = self._cachedIndex

        t1 = pp[   i1   ] if i1 < len_pp else None
        t0 = pp[ i1 - 1 ] if i1 > 0 else None

        right = None

        goto = ''
        if t1 is None or t >= t1:
            giveUpAt = i1 + 2
            while True:
                if t1 is None:
                    if t < t0:
                        goto = 'forward_scan'
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
                    goto ="seek"
                    break

            # prepare binary search on the right side of the index
            if goto == '':
                right = len_pp
                goto = "linear_scan"

        if goto == 'forward_scan':
            goto = ''

        if goto == '' and (t0 is None or t < t0):
            got = ''
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
                    goto = "seek"
                    break

            # prepare binary search on the left side of the index
            if goto == '':
                right = i1
                i1 = 0
                goto = "linear_scan"

        # the interval is valid
        if goto == '':
            goto = "validate_interval"

        if goto == 'linear_scan':
            goto = ''

        # binary search
        if goto == '':
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

        if goto == "" or goto == "seek":
            self._cachedIndex = i1
            self.intervalChanged_(i1, t0, t1)

        return self.interpolate_( i1, t0, t, t1 )

    def getSettings_(self):
        return self.settings or self.DefaultSettings_

    def copySampleValue_(self, index, t0=None, t1=None ):
        # copies a sample value to the result buffer

        result = self.resultBuffer
        values = self.sampleValues
        stride = self.valueSize
        offset = index * stride

        for i in range(stride):
            result[ i ] = values[ offset + i ]

        return result

    # Template methods for derived classes:

    def interpolate_(self, i1, t0, t, t1 ):
        raise RuntimeError( "call to abstract method" )
        # implementations shall return self.resultBuffer

    def intervalChanged_( self, i1, t0, t1 ):
        # empty
        return
