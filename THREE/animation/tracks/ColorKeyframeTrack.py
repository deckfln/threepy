"""
 * A Track of keyframe values that represent color.
 *
 *
 * @author Ben Houston / http://clara.io/
 * @author David Sarno / http://lighthaus.us/
 * @author tschw
"""
from THREE.animation.KeyframeTrack import *


class ColorKeyframeTrack(KeyframeTrack):
    """
     * A Track of keyframe values that represent color.
     *
     *
     * @author Ben Houston / http://clara.io/
     * @author David Sarno / http://lighthaus.us/
     * @author tschw
    """
    ValueTypeName = 'color'

    # ValueBufferType is inherited
    # DefaultInterpolation is inherited

    def __init__(self, name, times, values, interpolation=None):
        super().__init__(name, times, values, interpolation)

        # Note: Very basic implementation and nothing special yet.
        # However, this is the place for color space parameterization.

