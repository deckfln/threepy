"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 *
 * parameters = {
 *  color: <hex>,
 *  opacity: <float>,
 *
 *  linewidth: <float>,
 *  linecap: "round",
 *  linejoin: "round"
 * }
 */
"""
from THREE.materials.Material import *
from THREE.math.Color import *


class LineBasicMaterial(Material):
    isLineBasicMaterial = True

    def __init__(self, parameters=None ):
        super().__init__()
        self.set_class(isLineBasicMaterial)

        self.type = 'LineBasicMaterial'

        self.color = Color( 0xffffff )

        self.linewidth = 1
        self.linecap = 'round'
        self.linejoin = 'round'

        self.lights = False

        self.setValues( parameters )

    def copy(self, source ):
        super().copy( source )

        self.color.copy( source.color )

        self.linewidth = source.linewidth
        self.linecap = source.linecap
        self.linejoin = source.linejoin

        return self
