"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 */
"""
import random
from THREE.Object3D import *
from THREE.Matrix4 import *
from THREE.Sphere import *
from THREE.Sphere import *
from THREE.Vector3 import *
from THREE.BufferGeometry import *
from THREE.LineBasicMaterial import *


class Line(Object3D):
    isLine = True
    
    def __init__(self, geometry=None, material=None, mode=0 ):
        super().__init__()
        if mode == 1:
            print( 'THREE.Line: parameter THREE.LinePieces no longer supported. Created THREE.LineSegments instead.' )
            return LineSegments( geometry, material )

        self.type = 'Line'

        self.geometry = geometry if geometry else BufferGeometry()
        self.material = material if material else LineBasicMaterial( { 'color': random.random() * 0xffffff } )

    def raycast(self, raycaster, intersects):
        inverseMatrix = Matrix4()
        ray = Ray()
        sphere = Sphere()

        precision = raycaster.linePrecision
        precisionSq = precision * precision

        geometry = self.geometry
        matrixWorld = self.matrixWorld

        # // Checking boundingSphere distance to ray

        if geometry.boundingSphere is None:
            geometry.computeBoundingSphere()

        sphere.copy( geometry.boundingSphere )
        sphere.applyMatrix4( matrixWorld )

        if raycaster.ray.intersectsSphere( sphere ) == False:
            return

        # //

        inverseMatrix.getInverse( matrixWorld )
        ray.copy( raycaster.ray ).applyMatrix4( inverseMatrix )

        vStart = Vector3()
        vEnd = Vector3()
        interSegment = Vector3()
        interRay = Vector3()
        step = 2 if (self and self.isLineSegments) else 1

        if geometry.isBufferGeometry:
            index = geometry.index
            attributes = geometry.attributes
            positions = attributes.position.array

            if index is not None:
                indices = index.array

                for i in range(0, len(indices) - 1, step):
                    a = indices[ i ]
                    b = indices[ i + 1 ]

                    vStart.fromArray( positions, a * 3 )
                    vEnd.fromArray( positions, b * 3 )

                    distSq = ray.distanceSqToSegment( vStart, vEnd, interRay, interSegment )

                    if distSq > precisionSq:
                        continue

                    interRay.applyMatrix4( self.matrixWorld )     # //Move back to world space for distance calculation

                    distance = raycaster.ray.origin.distanceTo( interRay )

                    if distance < raycaster.near or distance > raycaster.far:
                        continue

                    intersects.append( {
                        'distance': distance,
                        # // What do we want? intersection point on the ray or on the segment??
                        # // point: raycaster.ray.at( distance ),
                        'point': interSegment.clone().applyMatrix4( self.matrixWorld ),
                        'index': i,
                        'face': None,
                        'faceIndex': None,
                        'object': self
                    } )

            else:
                for i in range(0, positions.length / 3 - 1, step):
                    vStart.fromArray( positions, 3 * i )
                    vEnd.fromArray( positions, 3 * i + 3 )

                    distSq = ray.distanceSqToSegment( vStart, vEnd, interRay, interSegment )

                    if distSq > precisionSq:
                        continue

                    interRay.applyMatrix4( self.matrixWorld )     # //Move back to world space for distance calculation

                    distance = raycaster.ray.origin.distanceTo( interRay )

                    if distance < raycaster.near or distance > raycaster.far:
                        continue

                    intersects.append( {

                        'distance': distance,
                        # // What do we want? intersection point on the ray or on the segment??
                        # // point: raycaster.ray.at( distance ),
                        'point': interSegment.clone().applyMatrix4( self.matrixWorld ),
                        'index': i,
                        'face': None,
                        'faceIndex': None,
                        'object': self
                    } )

        elif geometry.isGeometry:
            vertices = geometry.vertices
            nbVertices = vertices.length

            for i in range(0, nbVertices - 1, step):
                distSq = ray.distanceSqToSegment( vertices[ i ], vertices[ i + 1 ], interRay, interSegment )

                if distSq > precisionSq:
                    continue

                interRay.applyMatrix4( self.matrixWorld )     # //Move back to world space for distance calculation

                distance = raycaster.ray.origin.distanceTo( interRay )

                if distance < raycaster.near or distance > raycaster.far:
                    continue

                intersects.append( {
                    'distance': distance,
                    # // What do we want? intersection point on the ray or on the segment??
                    # // point: raycaster.ray.at( distance ),
                    'point': interSegment.clone().applyMatrix4( self.matrixWorld ),
                    'index': i,
                    'face': None,
                    'faceIndex': None,
                    'object': self
                } )

    def clone(self):
        return Line( self.geometry, self.material ).copy( self )
