"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 */
"""
from THREE.Object3D import *
from THREE.Color import *
from THREE.Vector2 import *
from THREE.Matrix4 import *


class Light(Object3D):
    isLight = True
    
    def __init__(self, color=0xffffff, intensity=1 ):
        super().__init__()

        self.type = 'Light'

        self.color = Color( color )
        self.intensity = intensity

        self.receiveShadow = None
        self.distance = None
        self.shadow = None

    def copy(self, source ):
        super().copy( source )

        self.color.copy( source.color )
        self.intensity = source.intensity

        return self

    def toJSON(self, meta ):
        data = super().toJSON(meta )

        data.object.color = self.color.getHex()
        data.object.intensity = self.intensity

        if self.groundColor is not None:
            data.object.groundColor = self.groundColor.getHex()

        if self.distance is not None:
            data.object.distance = self.distance
        
        if self.angle is not None:
            data.object.angle = self.angle

        if self.decay is not None:
            data.object.decay = self.decay

        if self.penumbra is not None:
            data.object.penumbra = self.penumbra

        if self.shadow is not None:
            data.object.shadow = self.shadow.toJSON()

        return data;


"""        
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""


class LightShadow(pyOpenGLObject):
    def __init__(self, camera):
        self.camera = camera

        self.bias = 0
        self.radius = 1

        self.mapSize = Vector2( 512, 512 )

        self.map = None
        self.matrix = Matrix4()

    def copy(self, source ):
        self.camera = source.camera.clone()

        self.bias = source.bias
        self.radius = source.radius

        self.mapSize.copy( source.mapSize )

        return self

    def clone(self):
        return type(self)().copy( self )

    def toJSON(self):
        object = {}

        if self.bias != 0:
            object.bias = self.bias
        if self.radius != 1:
            object.radius = self.radius
        if self.mapSize.x != 512 or self.mapSize.y != 512:
            object.mapSize = self.mapSize.toArray()

        object.camera = self.camera.toJSON( False ).object
        del object.camera.matrix

        return object
