"""
 * @author mikael emtinger / http:#gomo.se/
 * @author alteredq / http:#alteredqualia.com/
 * @author michael guerrero / http:#realitymeltdown.com
 * @author ikerr / http:#verold.com
"""
from THREE.javascriparray import *
from THREE.Matrix4 import *


class Skeleton:
    def __init__(self, bones, boneInverses=None ):
        # copy the bone array
        bones = bones or []

        self.bones = bones[:]
        self.boneMatrices = Float32Array( len(self.bones) * 16 )
        self.boneTexture = None

        # use the supplied bone inverses or calculate the inverses
        if boneInverses is None:
            self.calculateInverses()

        else:
            if len(self.bones) == len(boneInverses):
                self.boneInverses = boneInverses[:]

            else:
                print( 'THREE.Skeleton boneInverses is the wrong length.' )

                self.boneInverses = []
                for i in range(len(self.bones)):
                    self.boneInverses.append( Matrix4() )

    def calculateInverses(self):
        self.boneInverses = []

        for bone in self.bones:
            inverse = Matrix4()

            if bone:
                inverse.getInverse( bone.matrixWorld )

            self.boneInverses.append( inverse )

    def pose(self):
        # recover the bind-time world matrices
        for i in range(len(self.bones)):
            bone = self.bones[ i ]

            if bone:
                bone.matrixWorld.getInverse( self.boneInverses[ i ] )

        # compute the local matrices, positions, rotations and scales
        for bone in self.bones:
            if bone:
                if bone.parent and bone.parent.isBone:
                    bone.matrix.getInverse( bone.parent.matrixWorld )
                    bone.matrix.multiply( bone.matrixWorld )

                else:
                    bone.matrix.copy( bone.matrixWorld )

                bone.matrix.decompose( bone.position, bone.quaternion, bone.scale )

    def update(self):
        offsetMatrix = Matrix4()
        identityMatrix = Matrix4()

        bones = self.bones
        boneInverses = self.boneInverses
        boneMatrices = self.boneMatrices
        boneTexture = self.boneTexture

        # flatten bone matrices to array
        for i in range(len(bones)):
            # compute the offset between the current and the original transform
            matrix = bones[ i ].matrixWorld if bones[ i ] else identityMatrix

            offsetMatrix.multiplyMatrices( matrix, boneInverses[ i ] )
            offsetMatrix.toArray( boneMatrices, i * 16 )

        if boneTexture is not None:
            boneTexture.needsUpdate = True

    def clone(self):
        return Skeleton( self.bones, self.boneInverses )
