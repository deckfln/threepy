"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 */
"""
from THREE.Vector3 import *
from THREE.Color import *


class Face3:
    def __init__(self, a=None, b=None, c=None, normal=None, color=None, materialIndex=0 ):
        self.a = a
        self.b = b
        self.c = c

        if isinstance( normal, list):
            self.vertexNormals = normal
            self.normal = Vector3()
        elif normal and normal.isVector3:
            self.normal = normal
            self.vertexNormals = []
        else:
            self.normal = Vector3()
            self.vertexNormals = []

        if isinstance( color, list):
            self.vertexColors = color
            self.color = Color()
        elif color and color.isVector3:
            self.color = color
            self.vertexColors = []
        else:
            self.color = Vector3()
            self.vertexColors= []

        self.materialIndex = materialIndex

    def clone(self):
        return type(self)().copy( self )

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
