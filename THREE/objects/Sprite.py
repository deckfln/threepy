"""
/**
 * @author mikael emtinger / http://gomo.se/
 * @author alteredq / http://alteredqualia.com/
 */
"""
from THREE.core.BufferGeometry import *
from THREE.core.InterleavedBufferAttribute import *
from THREE.materials.SpriteMaterial import *
from THREE.javascriparray import *

_geometry = None


class Sprite(Object3D):
    isSprite = True
    
    def __init__(self, material=None ):
        global _geometry
        super().__init__()
        self.set_class(isSprite)

        self.type = 'Sprite'

        if _geometry is None:
            _geometry = BufferGeometry()

            float32Array = Float32Array( [
                - 0.5, - 0.5, 0, 0, 0,
                0.5, - 0.5, 0, 1, 0,
                0.5, 0.5, 0, 1, 1,
                - 0.5, 0.5, 0, 0, 1
            ] )

            interleavedBuffer = InterleavedBuffer( float32Array, 5 )

            _geometry.setIndex( [ 0, 1, 2,	0, 2, 3 ] )
            _geometry.addAttribute( 'position', InterleavedBufferAttribute( interleavedBuffer, 3, 0, False ) )
            _geometry.addAttribute( 'uv', InterleavedBufferAttribute( interleavedBuffer, 2, 3, False ) )

        self.geometry = _geometry

        self.material = material if material else SpriteMaterial()

        self.center = Vector2(0.5, 0.5)

    def raycast(self, raycaster, intersects):
        intersectPoint = Vector3()
        worldScale = Vector3()
        mvPosition = Vector3()

        alignedPosition = Vector2()
        rotatedPosition = Vector2()
        viewWorldMatrix = Matrix4()

        vA = Vector3()
        vB = Vector3()
        vC = Vector3()

        def transformVertex( vertexPosition, mvPosition, center, scale, sin, cos ):
            # compute position in camera space
            alignedPosition.subVectors( vertexPosition, center ).addScalar( 0.5 ).multiply( scale )

            # to check if rotation is not zero
            if sin is not None:
                rotatedPosition.x = ( cos * alignedPosition.x ) - ( sin * alignedPosition.y )
                rotatedPosition.y = ( sin * alignedPosition.x ) + ( cos * alignedPosition.y )

            else:
                rotatedPosition.copy( alignedPosition )

            vertexPosition.copy( mvPosition )
            vertexPosition.x += rotatedPosition.x
            vertexPosition.y += rotatedPosition.y

            # transform to world space
            vertexPosition.applyMatrix4( viewWorldMatrix )

        worldScale.setFromMatrixScale( self.matrixWorld )
        viewWorldMatrix.getInverse( self.modelViewMatrix ).premultiply( self.matrixWorld )
        mvPosition.setFromMatrixPosition( self.modelViewMatrix )

        rotation = self.material.rotation
        if rotation != 0:
            cos = math.cos( rotation )
            sin = math.sin( rotation )

        center = self.center

        transformVertex( vA.set( - 0.5, - 0.5, 0 ), mvPosition, center, worldScale, sin, cos )
        transformVertex( vB.set( 0.5, - 0.5, 0 ), mvPosition, center, worldScale, sin, cos )
        transformVertex( vC.set( 0.5, 0.5, 0 ), mvPosition, center, worldScale, sin, cos )

        # check first triangle
        intersect = raycaster.ray.intersectTriangle( vA, vB, vC, False, intersectPoint )

        if intersect is None:
            # check second triangle
            transformVertex( vB.set( - 0.5, 0.5, 0 ), mvPosition, center, worldScale, sin, cos )
            intersect = raycaster.ray.intersectTriangle( vA, vC, vB, False, intersectPoint )
            if intersect is None:
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

    def copy(self, source):
        super().copy(source)
        if source.center is not None:
            self.center.copy( source.center )

        return self
