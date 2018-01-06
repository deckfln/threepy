"""
 * @author Sean Griffin / http://twitter.com/sgrif
 * @author Michael Guerrero / http://realitymeltdown.com
 * @author mrdoob / http://mrdoob.com/
 * @author ikerr / http://verold.com
 * @author Mugen87 / https://github.com/Mugen87
"""
from THREE.LineSegments import *


def getBoneList( object ):
    boneList = []

    if object and object.isBone:
        boneList.append( object )

    for child in object.children:
        boneList.append.apply( boneList, getBoneList( child ) )

    return boneList


class SkeletonHelper(LineSegments):
    def __init__(self, object ):
        bones = getBoneList( object )

        geometry = ufferGeometry()

        vertices = []
        colors = []

        color1 = Color( 0, 0, 1 )
        color2 = Color( 0, 1, 0 )

        for bone in bones:
            if bone.parent and bone.parent.isBone:
                vertices.append( 0, 0, 0 )
                vertices.append( 0, 0, 0 )
                colors.append( color1.r, color1.g, color1.b )
                colors.append( color2.r, color2.g, color2.b )

        geometry.addAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        geometry.addAttribute( 'color', Float32BufferAttribute( colors, 3 ) )

        material = LineBasicMaterial( { 'vertexColors': VertexColors, 'depthTest': False, 'depthWrite': False, 'transparent': True } );

        super().__init__( self, geometry, material )

        self.root = object
        self.bones = bones

        self.matrix = object.matrixWorld
        self.matrixAutoUpdate = False

        self.onBeforeRender()

    def onBeforeRender(self):
        vector = Vector3()

        boneMatrix = Matrix4()
        matrixWorldInv = Matrix4()

        bones = self.bones
        geometry = self.geometry;
        position = geometry.getAttribute( 'position' )

        matrixWorldInv.getInverse( self.root.matrixWorld )

        j=0
        for bone in bones:
            if bone.parent and bone.parent.isBone:
                boneMatrix.multiplyMatrices( matrixWorldInv, bone.matrixWorld )
                vector.setFromMatrixPosition( boneMatrix )
                position.setXYZ( j, vector.x, vector.y, vector.z )

                boneMatrix.multiplyMatrices( matrixWorldInv, bone.parent.matrixWorld )
                vector.setFromMatrixPosition( boneMatrix )
                position.setXYZ( j + 1, vector.x, vector.y, vector.z )

                j += 2

        geometry.getAttribute( 'position' ).needsUpdate = True
