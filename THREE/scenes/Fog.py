"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 */
"""
from THREE.math.Color import *

"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 */
"""


class Fog(pyOpenGLObject):
    isFog = True
    
    def __init__(self, color, near=1, far=1000 ):
        super().__init__()
        self.set_class(isFog)
        self.name = ''

        self.color = Color( color )

        self.near = near
        self.far = far

    def clone(self):
        return type(self)( self.color, self.near, self.far )

    def toJSON(self):
        return {
            'type': 'Fog',
            'color': self.color.getHex(),
            'near': self.near,
            'far': self.far
        }
