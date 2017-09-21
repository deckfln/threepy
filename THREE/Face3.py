"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 */
"""
from THREE.Vector3 import *
from THREE.Color import *


class Face3:
    def __init__(self, a=None, b=None, c=None, normal=None, color=None, materialIndex=None ):
        self.a = a
        self.b = b
        self.c = c

        self.normal = normal if ( normal and hasattr(normal, 'isVector3' )) else Vector3()
        self.vertexNormals = normal if type( normal ) == 'array' else []

        self.color = color if ( color and hasattr(color, 'isColor')) else Color()
        self.vertexColors = color if type(color) == 'array' else []

        self.materialIndex = materialIndex if materialIndex is not None else 0

    def clone(self):
        return Face3().copy( self )

    def copy(self, source ):
        self.a = source.a
        self.b = source.b
        self.c = source.c

        self.normal.copy( source.normal )
        self.color.copy( source.color )

        self.materialIndex = source.materialIndex

        for i in range(len(source.vertexNormals)):
            self.vertexNormals[ i ] = source.vertexNormals[ i ].clone()

        for i in range(len(source.vertexColors)):
            self.vertexColors[ i ] = source.vertexColors[ i ].clone()

        return self
