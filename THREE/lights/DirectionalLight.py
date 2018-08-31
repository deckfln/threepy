"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.lights.Light import *
from THREE.cameras.OrthographicCamera import *


class DirectionalLightShadow(LightShadow):
    def __init__(self):
        super().__init__(OrthographicCamera(-5, 5, 5, -5, 0.5, 500))


"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 */
"""


class DirectionalLight(Light):
    isDirectionalLight = True
    
    def __init__(self, color=0xffffff, intensity=1):
        super().__init__(color, intensity)
        self.set_class(isDirectionalLight)

        self.type = 'DirectionalLight'

        self.position.copy(Object3D.DefaultUp)
        self.updateMatrix()

        self.target = Object3D()

        self.shadow = DirectionalLightShadow()

    def copy(self, source):
        super().copy(source)

        self.target = source.target.clone()

        self.shadow = source.shadow.clone()

        return self
