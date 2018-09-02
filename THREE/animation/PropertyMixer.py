"""
 *
 * Buffered scene graph property that allows weighted accumulation.
 *
 *
 * @author Ben Houston / http:#clara.io/
 * @author David Sarno / http:#lighthaus.us/
 * @author tschw
"""
from THREE.javascriparray import *
from THREE.math.Quaternion import *


class PropertyMixer:
    def __init__(self, binding, typeName, valueSize ):
        self.binding = binding
        self.valueSize = int(valueSize)

        bufferType = Float32Array

        if typeName == 'quaternion':
            mixFunction = self._slerp

        elif typeName =='string' or typeName == 'bool':
            bufferType = Array
            mixFunction = self._select

        else:
            mixFunction = self._lerp

        self.buffer = bufferType( valueSize * 4 )
        # layout: [ incoming | accu0 | accu1 | orig ]
        #
        # interpolators can use .buffer as their .result
        # the data then goes to 'incoming'
        #
        # 'accu0' and 'accu1' are used frame-interleaved for
        # the cumulative result and are compared to detect
        # changes
        #
        # 'orig' stores the original state of the property

        self._mixBufferRegion = mixFunction

        self.cumulativeWeight = 0

        self.useCount = 0
        self.referenceCount = 0

    def accumulate(self, accuIndex, weight ):
        """
        # accumulate data in the 'incoming' region into 'accu<i>'
        # note: happily accumulating nothing when weight = 0, the caller knows
        # the weight and shouldn't have made the call in the first place
        """
        buffer = self.buffer
        stride = self.valueSize
        offset = accuIndex * stride + stride

        currentWeight = self.cumulativeWeight

        if currentWeight == 0:
            # accuN := incoming * weight
            for i in range(stride):
                buffer[ offset + i ] = buffer[ i ]

            currentWeight = weight

        else:
            # accuN := accuN + incoming * weight
            currentWeight += weight
            mix = weight / currentWeight
            self._mixBufferRegion( buffer, offset, 0, mix, stride )

        self.cumulativeWeight = currentWeight

    def apply(self, accuIndex ):
        """
        # apply the state of 'accu<i>' to the binding when accus differ
        """
        stride = self.valueSize
        buffer = self.buffer
        offset = accuIndex * stride + stride

        weight = self.cumulativeWeight

        binding = self.binding

        self.cumulativeWeight = 0

        if weight < 1:
            # accuN := accuN + original * ( 1 - cumulativeWeight )
            originalValueOffset = stride * 3

            self._mixBufferRegion(
                buffer, offset, originalValueOffset, 1 - weight, stride )

        for i in range(stride, stride + stride):
            if buffer[ i ] != buffer[ i + stride ]:
                # value has changed -> update scene graph
                binding.setValue( buffer, offset )
                break

    def saveOriginalState(self):
        """
        # remember the state of the bound property and copy it to both accus
        """
        binding = self.binding

        buffer = self.buffer
        stride = self.valueSize

        originalValueOffset = int(stride * 3)

        binding.getValue( buffer, originalValueOffset )

        # accu[0..1] := orig -- initially detect changes against the original
        for i in range(stride, originalValueOffset):
            buffer[ i ] = buffer[ originalValueOffset + ( i % stride ) ]

        self.cumulativeWeight = 0

    def restoreOriginalState(self):
        """
        # apply the state previously taken via 'saveOriginalState' to the binding
        """
        originalValueOffset = int(self.valueSize * 3)
        self.binding.setValue( self.buffer, originalValueOffset )

    # mix functions

    def _select(self, buffer, dstOffset, srcOffset, t, stride ):
        if t >= 0.5:
            for i in range(stride):
                buffer[ dstOffset + i ] = buffer[ srcOffset + i ]

    def _slerp(self, buffer, dstOffset, srcOffset, t, stride=None ):
        Quaternion.slerpFlat( None, buffer, dstOffset, buffer, dstOffset, buffer, srcOffset, t )

    def _lerp(self, buffer, dstOffset, srcOffset, t, stride ):
        s = 1 - t

        for i in range(stride):
            j = dstOffset + i

            buffer[ j ] = buffer[ j ] * s + buffer[ srcOffset + i ] * t
