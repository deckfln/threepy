"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.Light import *
from THREE.Camera import *


class PointLight(Light):
    isPointLight = True
    
    def __init__(self, color, intensity, distance=0, decay=1 ):
        super().__init__(color, intensity )

        self.type = 'PointLight'

        self.distance = distance 
        self.decay = decay #    // for physically correct lights, should be 2.

        self.shadow = LightShadow( PerspectiveCamera( 90, 1, 0.5, 500 ) )

    def getPower(self):
        # // intensity = power per solid angle.
        # // ref: equation (15) from http://www.frostbite.com/wp-content/uploads/2014/11/course_notes_moving_frostbite_to_pbr.pdf
        return self.intensity * 4 * math.pi

    def setPower(self, power):
        # // intensity = power per solid angle.
        # // ref: equation (15) from http://www.frostbite.com/wp-content/uploads/2014/11/course_notes_moving_frostbite_to_pbr.pdf
        self.intensity = power / (4 * math.pi)

    power = property(getPower, setPower)
    
    def copy(self, source ):
        super().copy( source )

        self.distance = source.distance
        self.decay = source.decay

        self.shadow = source.shadow.clone()

        return self
