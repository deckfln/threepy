"""
 * A Track of vectored keyframe values.
 *
 *
 * @author Ben Houston / http://clara.io/
 * @author David Sarno / http://lighthaus.us/
 * @author tschw
"""

from THREE.animation.KeyframeTrack import *


class VectorKeyframeTrack(KeyframeTrack):
    """
     * A Track of vectored keyframe values.
     *
     *
     * @author Ben Houston / http://clara.io/
     * @author David Sarno / http://lighthaus.us/
     * @author tschw
    """
    ValueTypeName = 'vector'
    # ValueBufferType is inherited
    # DefaultInterpolation is inherited

    def __init__(self, name, times, values, interpolation=None):
        super().__init__(name, times, values, interpolation)
