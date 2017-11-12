"""

"""
from THREE.AnimationUtils import *
from THREE.Constants import *
from THREE.QuaternionLinearInterpolant import *


class KeyframeTrackConstructor:
    TimeBufferType = None
    ValueBufferType = None
    DefaultInterpolation = None

    def __init__(self, name, times, values, interpolation=None ):
        if name is None:
            raise RuntimeError( "track name is undefined" )

        if times is None or len(times) == 0:
            raise RuntimeError( "no keyframes in track named " + name )

        self.name = name

        self.times = AnimationUtils.convertArray( times, self.TimeBufferType )
        self.values = AnimationUtils.convertArray( values, self.ValueBufferType )
        self.createInterpolant = None

        self.setInterpolation( interpolation or self.DefaultInterpolation )

        self.validate()
        self.optimize()

    def validate(self):
        return
        
    def optimize(self):
        return

    def setInterpolation(self, interpolation):
        return


