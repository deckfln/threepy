"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.Line import *


class LineSegments(Line):
    isLineSegments = True
    
    def __init__(self, geometry=None, material=None ):
        super().__init__( geometry, material )

        self.type = 'LineSegments'
