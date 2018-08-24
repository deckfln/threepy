"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 */
"""
from THREE.pyOpenGLObject import *
from THREE.Color import *


class FogExp2(pyOpenGLObject):
    isFogExp2 = True
    
    def __init__(self, color, density ):
        super().__init__()
        self.set_class(isFogExp2)

        self.name = ''

        self.color = Color( color )
        self.density = density if density is not None else 0.00025

    def clone(self):
        return type(self)( self.color.getHex(), self.density )

    def toJSON(self, meta ):
        return {
            'type': 'FogExp2',
            'color': self.color.getHex(),
            'density': self.density
        }
