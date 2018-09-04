"""
 * @author tschw
 * @author Ben Houston / http://clara.io/
 * @author David Sarno / http://lighthaus.us/
"""
import numpy as np


class AnimationUtils:
    def arraySlice( array, fromm, to ):
        """
        # same as Array.prototype.slice, but also works on typed arrays
        """
        if AnimationUtils.isTypedArray( array ):
            # in ios9 array.subarray(from, undefined) will return empty array
            # but array.subarray(from) or array.subarray(from, len) is correct
            return array.constructor( array.subarray( fromm, to if to is not None else array.length ) )

        return array[fromm:to]

    def convertArray( array, type, forceClone=False ):
        """
        # converts an array to a specific type
        """
        array_is_an_instance_of_type = False
        if type == 'Float32Array' and isinstance(array, np.ndarray):
            if array.dtype.name == 'float32':
                array_is_an_instance_of_type = True

        if not array or not forceClone and array_is_an_instance_of_type:
            return array

        if 'Float' in type:
            cv = {
                'Float32Array': np.float32
            }
            return np.array(array, cv[type])    # create typed array

        return array[:]     # create Array

    def isTypedArray( object ):
        raise RuntimeWarning("wtf")
        # return ArrayBuffer.isView( object ) and not ( object instanceof DataView )

    def getKeyframeOrder( times ):
        """
        # returns an array by which times and values can be sorted
        """
        def compareTime( i):
            return times[ i ]

        n = len(times)
        result = [i for i in range(n)]

        result.sort( key=compareTime )

        return result

    def sortedArray( values, stride, order ):
        """
        # uses the array previously returned by 'getKeyframeOrder' to sort data
        """
        nValues = len(values)
        result = [ None for i in range( nValues )]

        dstOffset = 0
        i = 0
        while dstOffset != nValues:
            srcOffset = order[ i ] * stride

            for j in range(stride):
                result[ dstOffset ] = values[ srcOffset + j ]
                dstOffset += 1

            i += 1

        return result

    def flattenJSON( jsonKeys, times, values, valuePropertyName ):
        """
        # function for parsing AOS keyframe formats
        """
        i = 1
        key = jsonKeys[0]

        while key is not None and valuePropertyName not in key:
            key = jsonKeys[i]
            i += 1

        if key is None:
            return    # no data

        if valuePropertyName not in key:
            return    # no data

        value = key[valuePropertyName]
        if isinstance(value, list):
            for k in range(i, len(jsonKeys) + 1):
                key = jsonKeys[k - 1]
                if valuePropertyName in key:
                    value = key[valuePropertyName]

                    times.append(key['time'])
                    for v in value:
                       values.append(v)    # // push all elements

        elif 'toArray' in value:
            # ...assume THREE.Math-ish
            for k in range(i, len(jsonKeys) + 1):
                key = jsonKeys[k - 1]
                if valuePropertyName in key:
                    value = key[valuePropertyName]

                    times.append(key['time'])
                    value.toArray(values, len(values))

        else:
            # otherwise push as-is
            for k in range(i, len(jsonKeys) + 1):
                key = jsonKeys[k - 1]
                value = key[valuePropertyName]

                if value is not None:
                    times.append(key['time'])
                    values.append(value)
