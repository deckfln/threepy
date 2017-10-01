"""
/**
 * @author mikael emtinger / http://gomo.se/
 * @author alteredq / http://alteredqualia.com/
 */
"""
from THREE.Object3D import *
from THREE.SpriteMaterial import *


class Sprite(Object3D):
    isSprite = True
    
    def __init__(self, material=None ):
        super().__init__()

        self.type = 'Sprite'

        self.material = material if ( material ) else SpriteMaterial()

    def raycast(self, raycaster, intersects):
        intersectPoint = Vector3()
        worldPosition = Vector3()
        worldScale = Vector3()

        worldPosition.setFromMatrixPosition( self.matrixWorld )
        raycaster.ray.closestPointToPoint( worldPosition, intersectPoint )

        worldScale.setFromMatrixScale( self.matrixWorld )
        guessSizeSq = worldScale.x * worldScale.y / 4

        if worldPosition.distanceToSquared( intersectPoint ) > guessSizeSq:
            return

        distance = raycaster.ray.origin.distanceTo( intersectPoint )

        if raycaster.near < distance <  raycaster.far:
            intersects.append( {
                'distance': distance,
                'point': intersectPoint.clone(),
                'face': None,
                'object': self

            })

    def clone(self):
        return type(self)().copy( self )
