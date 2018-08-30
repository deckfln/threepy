"""
 * A Track that interpolates Strings
 *
 *
 * @author Ben Houston / http://clara.io/
 * @author David Sarno / http://lighthaus.us/
 * @author tschw
"""
from THREE.animation.KeyframeTrack import *


class StringKeyframeTrack(KeyframeTrack):
    """
     * A Track that interpolates Strings
     *
     *
     * @author Ben Houston / http://clara.io/
     * @author David Sarno / http://lighthaus.us/
     * @author tschw
    """
    ValueTypeName = 'string'
    ValueBufferType = list
    DefaultInterpolation = InterpolateDiscrete
    InterpolantFactoryMethodLinear = None
    InterpolantFactoryMethodSmooth = None

    def __init__(self, name, times, values, interpolation=None):
        super().__init__(name, times, values, interpolation)
