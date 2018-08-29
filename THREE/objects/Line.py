"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 */
"""
import random
from THREE.core.BufferGeometry import *
from THREE.materials.LineBasicMaterial import *


class Line(Object3D):
    isLine = True
    
    def __init__(self, geometry=None, material=None, mode=0 ):
        super().__init__()

        self.set_class(isLine)

        if mode == 1:
            raise RuntimeWarning( 'THREE.Line: parameter THREE.LinePieces no longer supported. Created THREE.LineSegments instead.' )

        self.type = 'Line'

        self.geometry = geometry if geometry else BufferGeometry()
        self.material = material if material else LineBasicMaterial( { 'color': random.random() * 0xffffff } )

    def computeLineDistances(self):
        start = Vector3()
        end = Vector3()
        geometry = self.geometry

        if geometry.is_class(isBufferGeometry):
            # we assume non-indexed geometry

            if geometry.index is None:
                positionAttribute = geometry.attributes.position
                lineDistances = [ 0 ]

                for i in range(1, positionAttribute.count):
                    start.fromBufferAttribute( positionAttribute, i - 1 )
                    end.fromBufferAttribute( positionAttribute, i )

                    lineDistances[ i ] = lineDistances[ i - 1 ]
                    lineDistances[ i ] += start.distanceTo( end )

                geometry.addAttribute( 'lineDistance', Float32BufferAttribute( lineDistances, 1 ) )

            else:
                raise RuntimeWarning( 'THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.' )

        elif geometry.is_class(isGeometry):
            vertices = geometry.vertices
            lineDistances = geometry.lineDistances

            lineDistances[ 0 ] = 0

            for i in range(1, len(vertices)):
                lineDistances[ i ] = lineDistances[ i - 1 ]
                lineDistances[ i ] += vertices[ i - 1 ].distanceTo( vertices[ i ] )

        return self

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
        step = 2 if (self and self.my_class(isLineSegments)) else 1

        if geometry.my_class(isBufferGeometry):
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

        elif geometry.my_class(isGeometry):
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
        return type(self)( self.geometry, self.material ).copy( self )
