"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author alteredq / http:# //alteredqualia.com/
 *
 * parameters = {
 *  color: <hex>,
 *  opacity: <float>,
 *  map: THREE.Texture( <Image> ),
 *
 *  size: <float>,
 *  sizeAttenuation: <bool>
 * }
 */
"""
import random

from THREE.materials.Material import *
from THREE.BufferGeometry import *
from THREE.math.Sphere import *
# TODO implement Ray
# from THREE.Ray import *


class PointsMaterial(Material):
    isPointsMaterial = True

    def __init__(self, parameters ):
        super().__init__( )
        self.set_class(isPointsMaterial)

        self.type = 'PointsMaterial'

        self.color = Color( 0xffffff )

        self.map = None

        self.size = 1
        self.sizeAttenuation = True

        self.lights = False

        self.setValues( parameters )

    def copy(self, source ):
        super().copy( source )

        self.color.copy( source.color )

        self.map = source.map

        self.size = source.size
        self.sizeAttenuation = source.sizeAttenuation

        return self

"""
/**
 * @author alteredq / http:# //alteredqualia.com/
 */
"""


class Points(Object3D):
    isPoints = True
    
    def __init__(self, geometry=None, material=None ):
        super().__init__()
        self.set_class(isPoints)

        self.type = 'Points'

        self.geometry = geometry if geometry is not None else BufferGeometry()
        self.material = material if material is not None else PointsMaterial( { 'color': random.random() * 0xffffff } )

    def raycast(self, raycaster, intersects):
        inverseMatrix = Matrix4()
        ray = Ray()
        sphere = Sphere()

        object = self
        geometry = self.geometry
        matrixWorld = self.matrixWorld
        threshold = raycaster.params.Points.threshold

        # // Checking boundingSphere distance to ray

        if geometry.boundingSphere == None:
            geometry.computeBoundingSphere()

        sphere.copy( geometry.boundingSphere )
        sphere.applyMatrix4( matrixWorld )
        sphere.radius += threshold

        if raycaster.ray.intersectsSphere( sphere ) == False:
            return

        # //

        inverseMatrix.getInverse( matrixWorld )
        ray.copy( raycaster.ray ).applyMatrix4( inverseMatrix )

        localThreshold = threshold / ( ( self.scale.x + self.scale.y + self.scale.z ) / 3 )
        localThresholdSq = localThreshold * localThreshold
        position = Vector3()

        def testPoint( point, index ):
            rayPointDistanceSq = ray.distanceSqToPoint( point )

            if rayPointDistanceSq < localThresholdSq:
                intersectPoint = ray.closestPointToPoint( point )
                intersectPoint.applyMatrix4( matrixWorld )

                distance = raycaster.ray.origin.distanceTo( intersectPoint )

                if distance < raycaster.near or distance > raycaster.far:
                    return

                intersects.append( {
                    'distance': distance,
                    'distanceToRay': math.sqrt( rayPointDistanceSq ),
                    'point': intersectPoint.clone(),
                    'index': index,
                    'face': None,
                    'object': object
                } )

        if geometry.is_('BufferGeometry'):
            index = geometry.index
            attributes = geometry.attributes
            positions = attributes.position.array

            if index is not None:
                indices = index.array

                for i in range(len(indices)):
                    a = indices[ i ]

                    position.fromArray( positions, a * 3 )

                    testPoint( position, a )

            else:
                for i in range(int(len(positions) / 3)):
                    position.fromArray( positions, i * 3 )

                    testPoint( position, i )

        else:
            vertices = geometry.vertices

            for i in range(len(vertices)):
                testPoint( vertices[ i ], i )

    def clone(self, recursive=True):
        return type(self)( self.geometry, self.material ).copy( self )
