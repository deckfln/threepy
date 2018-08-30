"""
 * A Track of quaternion keyframe values.
 *
 * @author Ben Houston / http://clara.io/
 * @author David Sarno / http://lighthaus.us/
 * @author tschw
"""
from THREE.animation.KeyframeTrack import *
from THREE.math.interpolants.QuaternionLinearInterpolant import *


class QuaternionKeyframeTrack(KeyframeTrack):
    """
     * A Track of quaternion keyframe values.
     *
     * @author Ben Houston / http://clara.io/
     * @author David Sarno / http://lighthaus.us/
     * @author tschw
    """
    ValueTypeName = 'quaternion'
    # ValueBufferType is inherited
    DefaultInterpolation = InterpolateLinear
    InterpolantFactoryMethodSmooth = None  # not yet implemented

    def __init__(self, name, times, values, interpolation=None):
        super().__init__(name, times, values, interpolation)

    def InterpolantFactoryMethodLinear(self, result):
        return QuaternionLinearInterpolant(self.times, self.values, self.getValueSize(), result)
