"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 * @author mikael emtinger / http://gomo.se/
 * @author jonobr1 / http://jonobr1.com/
 */
"""
import random
import math

from THREE.Constants import *
from THREE.Object3D import *
from THREE.MeshBasicMaterial import *
from THREE.Vector2 import *
from THREE.Vector3 import *
from THREE.Matrix4 import *
from THREE.Triangle import *
from THREE.Sphere import *
from THREE.BufferGeometry import *
from THREE.Face3 import *
from THREE.Ray import *


def _uvIntersection( point, p1, p2, p3, uv1, uv2, uv3 ):
    tr = Triangle(p1, p2, p3)
    barycoord = tr.barycoordFromPoint( point )

    uv1.multiplyScalar( barycoord.x )
    uv2.multiplyScalar( barycoord.y )
    uv3.multiplyScalar( barycoord.z )

    uv1.add( uv2 ).add( uv3 )

    return uv1.clone()

    
def _checkIntersection( object, material, raycaster, ray, pA, pB, pC, point ):
    if material.side == BackSide:
        intersect = ray.intersectTriangle( pC, pB, pA, True, point )
    else:
        intersect = ray.intersectTriangle( pA, pB, pC, material.side != DoubleSide, point )

    if intersect is None:
        return None

    intersectionPointWorld = point.clone()
    intersectionPointWorld.applyMatrix4( object.matrixWorld )

    distance = raycaster.ray.origin.distanceTo( intersectionPointWorld )

    if distance < raycaster.near or distance > raycaster.far:
        return None

    class _intersection:
        def __init__(self, distance, point, object):
            self.distance = distance
            self.point = point
            self.object = object
            self.uv = None

    return _intersection(distance, intersectionPointWorld.clone(), object)

    
def _checkBufferGeometryIntersection( object, raycaster, ray, position, uv, a, b, c ):
    vA = Vector3().fromBufferAttribute( position, a )
    vB = Vector3().fromBufferAttribute( position, b )
    vC = Vector3().fromBufferAttribute( position, c )

    intersection = _checkIntersection( object, object.material, raycaster, ray, vA, vB, vC, Vector3() )

    if intersection:
        if uv:
            uvA = Vector2().fromBufferAttribute( uv, a )
            uvB = Vector2().fromBufferAttribute( uv, b )
            uvC = Vector2().fromBufferAttribute( uv, c )

            intersection.uv = _uvIntersection( Vector3(), vA, vB, vC, uvA, uvB, uvC )

        triangle = Triangle(vA, vB, vC)
        intersection.face = Face3( a, b, c, triangle.normal( ) )
        intersection.faceIndex = a

    return intersection

    
class Mesh(Object3D):
    isMesh = True
    
    def __init__(self, geometry=None, material=None ):
        super().__init__()

        self.set_class(isMesh)

        self.type = 'Mesh'

        self.geometry = geometry if geometry is not None else BufferGeometry()
        self.material = material if material is not None else MeshBasicMaterial( { 'color': random.random() * 0xffffff } )

        self.drawMode = TrianglesDrawMode

        self.updateMorphTargets()

    def __getitem__(self, item):
        return self.__dict__[item]

    def setDrawMode(self, value ):
        self.drawMode = value

    def copy(self, source ):
        super().copy( source )

        self.drawMode = source.drawMode

        return self

    def updateMorphTargets(self):
        geometry = self.geometry

        if geometry.my_class(isBufferGeometry):
            morphAttributes = geometry.morphAttributes
            k = morphAttributes.keys()

            if len(k) > 0:
                morphAttribute = morphAttributes[ k[ 0 ] ]

                if morphAttribute is not None:
                    self.morphTargetInfluences = []
                    self.morphTargetDictionary = {}

                    for m in range(len(morphAttribute)):
                        name = morphAttribute[ m ].name or str( m )

                        self.morphTargetInfluences.append( 0 )
                        self.morphTargetDictionary[ name ] = m

        else:
            morphTargets = geometry.morphTargets

            if morphTargets is not None and len(morphTargets) > 0:
                self.morphTargetInfluences = []
                self.morphTargetDictionary = {}

                for m in range(len(morphTargets)):
                    name = morphTargets[ m ].name or str( m )

                    self.morphTargetInfluences.append( 0 )
                    self.morphTargetDictionary[ name ] = m

    def raycast(self, raycaster, intersects):
        inverseMatrix = Matrix4()
        ray = Ray()
        sphere = Sphere()

        vA = Vector3()
        vB = Vector3()
        vC = Vector3()

        tempA = Vector3()
        tempB = Vector3()
        tempC = Vector3()

        uvA = Vector2()
        uvB = Vector2()
        uvC = Vector2()

        barycoord = Vector3()

        intersectionPoint = Vector3()
        intersectionPointWorld = Vector3()

        geometry = self.geometry
        material = self.material
        matrixWorld = self.matrixWorld

        if material is None:
            return

        # // Checking boundingSphere distance to ray

        if geometry.boundingSphere is None:
            geometry.computeBoundingSphere()

        sphere.copy( geometry.boundingSphere )
        sphere.applyMatrix4( matrixWorld )

        if not raycaster.ray.intersectsSphere( sphere ): 
            return

        # //

        inverseMatrix.getInverse( matrixWorld )
        ray.copy( raycaster.ray ).applyMatrix4( inverseMatrix )

        # // Check boundingBox before continuing

        if geometry.boundingBox is not None:
            if not ray.intersectsBox( geometry.boundingBox ):
                return

        if geometry.my_class(isBufferGeometry):
            index = geometry.index
            position = geometry.attributes.position
            uv = geometry.attributes.uv

            if index is not None:
                # // indexed buffer geometry
                for i in range(0, index.count, 3):
                    a = index.getX( i )
                    b = index.getX( i + 1 )
                    c = index.getX( i + 2 )

                    intersection = _checkBufferGeometryIntersection( self, raycaster, ray, position, uv, a, b, c )

                    if intersection:
                        intersection.faceIndex = math.floor( i / 3 ); # // triangle number in indices buffer semantics
                        intersects.push( intersection )
            else:
                # // non-indexed buffer geometry
                for i in range(0, position.count, 3 ):
                    a = i
                    b = i + 1
                    c = i + 2

                    intersection = _checkBufferGeometryIntersection( self, raycaster, ray, position, uv, a, b, c )

                    if intersection:
                        intersection.index = a  #// triangle number in positions buffer semantics
                        intersects.push( intersection )
        elif geometry.my_class(isGeometry):
            isMultiMaterial = isinstance(material, list)

            vertices = geometry.vertices
            faces = geometry.faces

            faceVertexUvs = geometry.faceVertexUvs[ 0 ]
            if len(faceVertexUvs)> 0:
                uvs = faceVertexUvs

            for f in range(len(faces)):
                face = faces[ f ]
                faceMaterial = material[ face.materialIndex ] if isMultiMaterial else material

                if faceMaterial is None:
                    continue

                fvA = vertices[ face.a ]
                fvB = vertices[ face.b ]
                fvC = vertices[ face.c ]

                if faceMaterial.morphTargets:
                    morphTargets = geometry.morphTargets
                    morphInfluences = self.morphTargetInfluences

                    vA.set( 0, 0, 0 )
                    vB.set( 0, 0, 0 )
                    vC.set( 0, 0, 0 )

                    for t in range(len(morphTargets)):
                        influence = morphInfluences[ t ]

                        if influence == 0:
                            continue

                        targets = morphTargets[ t ].vertices

                        vA.addScaledVector( tempA.subVectors( targets[ face.a ], fvA ), influence )
                        vB.addScaledVector( tempB.subVectors( targets[ face.b ], fvB ), influence )
                        vC.addScaledVector( tempC.subVectors( targets[ face.c ], fvC ), influence )

                    vA.add( fvA )
                    vB.add( fvB )
                    vC.add( fvC )

                    fvA = vA
                    fvB = vB
                    fvC = vC

                intersection = _checkIntersection( self, faceMaterial, raycaster, ray, fvA, fvB, fvC, intersectionPoint )

                if intersection:
                    if uvs and uvs[ f ]:
                        uvs_f = uvs[ f ]
                        uvA.copy( uvs_f[ 0 ] )
                        uvB.copy( uvs_f[ 1 ] )
                        uvC.copy( uvs_f[ 2 ] )

                        intersection.uv = _uvIntersection( intersectionPoint, fvA, fvB, fvC, uvA, uvB, uvC )

                    intersection.face = face
                    intersection.faceIndex = f
                    intersects.append( intersection )

    def clone(self):
        return type(self)(self.geometry, self.material ).copy( self )