"""
/**
 * @author alteredq / http://alteredqualia.com/
 *
 * parameters = {
 *  color: <hex>,
 *  opacity: <float>,
 *
 *  linewidth: <float>,
 *
 *  scale: <float>,
 *  dashSize: <float>,
 *  gapSize: <float>
 * }
 */
"""
from THREE.LineBasicMaterial import *


class LineDashedMaterial(LineBasicMaterial):
    isLineDashedMaterial = True
    
    def __init__(self, parameters=None ):
        super().__init__(  )

        self.type = 'LineDashedMaterial'

        self.scale = 1
        self.dashSize = 3
        self.gapSize = 1

        self.setValues( parameters )

    def copy (self, source ):
        super().copy( source )

        self.scale = source.scale
        self.dashSize = source.dashSize
        self.gapSize = source.gapSize

        return self
