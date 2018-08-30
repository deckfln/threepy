"""
 * A Track of Boolean keyframe values.
 *
 *
 * @author Ben Houston / http://clara.io/
 * @author David Sarno / http://lighthaus.us/
 * @author tschw
 */
"""
from THREE.animation.KeyframeTrack import *


class BooleanKeyframeTrack(KeyframeTrack):
    """
     * A Track of Boolean keyframe values.
     *
     *
     * @author Ben Houston / http://clara.io/
     * @author David Sarno / http://lighthaus.us/
     * @author tschw
    """
    ValueTypeName = 'bool'
    ValueBufferType = list
    DefaultInterpolation = InterpolateDiscrete
    InterpolantFactoryMethodLinear = None
    InterpolantFactoryMethodSmooth = None

    def __init__(self, name, times, values):
        super().__init__(name, times, values)

        # Note: Actually this track could have a optimized / compressed
        # representation of a single value and a custom interpolant that
        # computes "firstValue ^ isOdd( index )".


