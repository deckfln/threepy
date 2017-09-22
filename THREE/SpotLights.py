"""
/**
 * @author alteredq / http://alteredqualia.com/
 */
"""
import math
import THREE._Math as _Math
from THREE.Light import *
from THREE.Camera import *


class _power:
    def __init__(self, parent):
        self.parent = parent
        
    def get(self):
        """
            // intensity = power per solid angle.
            // ref: equation (17) from http://www.frostbite.com/wp-content/uploads/2014/11/course_notes_moving_frostbite_to_pbr.pdf
        """
        return self.parent.intensity * math.pi

    def set(self,  power):
        """
        // intensity = power per solid angle.
        // ref: equation (17) from http://www.frostbite.com/wp-content/uploads/2014/11/course_notes_moving_frostbite_to_pbr.pdf
        """
        self.parent.intensity = power / math.pi
    
    
class SpotLight(Light):
    isSpotLight = True
    
    def __init__(self, color, intensity=1, distance=0, angle=math.pi/3, penumbra=0, decay=1 ):
        super().__init__( color, intensity )

        self.type = 'SpotLight'

        self.position.copy( Object3D.DefaultUp )
        self.updateMatrix()

        self.target = Object3D()
        self.power = _power(self)
        
        self.distance = distance
        self.angle = angle
        self.penumbra = penumbra
        self.decay = decay     # // for physically correct lights, should be 2.

        self.shadow = SpotLightShadow()

    def copy(self, source):
        super().copy(source)

        self.distance = source.distance
        self.angle = source.angle
        self.penumbra = source.penumbra
        self.decay = source.decay

        self.target = source.target.clone()

        self.shadow = source.shadow.clone()

        return self


"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""


class SpotLightShadow(LightShadow):
    isSpotLightShadow = True
    
    def __init__(self):
        super().__init__(PerspectiveCamera( 50, 1, 0.5, 500 ))

    def update(self, light ):
        camera = self.camera

        fov = _Math.RAD2DEG * 2 * light.angle
        aspect = self.mapSize.width / self.mapSize.height
        far = light.distance or camera.far

        if fov != camera.fov or aspect != camera.aspect or far != camera.far:
            camera.fov = fov
            camera.aspect = aspect
            camera.far = far
            camera.updateProjectionMatrix()
