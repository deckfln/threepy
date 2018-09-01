"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.lights.Light import *
from THREE.cameras.PerspectiveCamera import *


class PointLight(Light):
    isPointLight = True
    
    def __init__(self, color=0xffffff, intensity=1, distance=0, decay=1 ):
        super().__init__(color, intensity )
        self.set_class(isPointLight)

        self.type = 'PointLight'

        self.distance = distance 
        self.decay = decay #    // for physically correct lights, should be 2.

        self.shadow = LightShadow( PerspectiveCamera( 90, 1, 0.5, 500 ) )

    def getPower(self):
        # // intensity = power per solid angle.
        # // ef: equation (15) from https://seblagarde.files.wordpress.com/2015/07/course_notes_moving_frostbite_to_pbr_v32.pdf
        return self.intensity * 4 * math.pi

    def setPower(self, power):
        # // intensity = power per solid angle.
        # // ef: equation (15) from https://seblagarde.files.wordpress.com/2015/07/course_notes_moving_frostbite_to_pbr_v32.pdf
        self.intensity = power / (4 * math.pi)

    power = property(getPower, setPower)
    
    def copy(self, source, recursive=True ):
        super().copy( source )

        self.distance = source.distance
        self.decay = source.decay

        self.shadow = source.shadow.clone()

        return self
