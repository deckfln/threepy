"""
 * @author mikael emtinger / http:#gomo.se/
 * @author alteredq / http:#alteredqualia.com/
 * @author ikerr / http:#verold.com
"""
from THREE.objects.Mesh import *
from THREE.objects.Bone import *
from THREE.objects.Skeleton import *


class SkinnedMesh(Mesh):
    isSkinnedMesh = True

    def __init__(self, geometry, material):
        super().__init__(geometry, material)
        self.set_class(isSkinnedMesh)

        self.type = 'SkinnedMesh'

        self.bindMode = 'attached'
        self.bindMatrix = Matrix4()
        self.bindMatrixInverse = Matrix4()
        self.skeleton = None

        bones = self.initBones()
        skeleton = Skeleton(bones)

        self.bind(skeleton, self.matrixWorld)

        self.normalizeSkinWeights()

    def initBones(self):
        bones = []

        if self.geometry and self.geometry.bones is not None:

            # first, create array of 'Bone' objects from geometry data
            for gbone in self.geometry.bones:
                # create 'Bone' object

                bone = Bone()
                bones.append(bone)

                # apply values

                bone.name = gbone.name
                bone.position.fromArray(gbone.pos)
                bone.quaternion.fromArray(gbone.rotq)
                if gbone.scl is not None:
                    bone.scale.fromArray(gbone.scl)

            # second, create bone hierarchy
            for gbone in self.geometry.bones:
                if gbone.parent != - 1 and gbone.parent is not None and bones[gbone.parent] is not None:
                    # subsequent bones in the hierarchy
                    bones[gbone.parent].add(bones[i])

                else:
                    # topmost bone, immediate child of the skinned mesh
                    self.add(bones[i])

        # now the bones are part of the scene graph and children of the skinned mesh.
        # let's update the corresponding matrices

        self.updateMatrixWorld(True)

        return bones

    def bind(self, skeleton, bindMatrix):
        self.skeleton = skeleton

        if bindMatrix is None:
            self.updateMatrixWorld(True)

            self.skeleton.calculateInverses()

            bindMatrix = self.matrixWorld

        self.bindMatrix.copy(bindMatrix)
        self.bindMatrixInverse.getInverse(bindMatrix)

    def pose(self):
        self.skeleton.pose()

    def normalizeSkinWeights(self):
        if self.geometry and self.geometry.my_class(isGeometry):
            for sw in self.geometry.skinWeights:
                scale = 1.0 / sw.manhattanLength()

                if scale != float("+inf"):
                    sw.multiplyScalar(scale)

                else:
                    sw.set(1, 0, 0, 0)     # do something reasonable

        elif self.geometry and self.geometry.my_class(isBufferGeometry):
            vec = Vector4()

            skinWeight = self.geometry.attributes.skinWeight

            for i in range(skinWeight.count):
                vec.x = skinWeight.getX(i)
                vec.y = skinWeight.getY(i)
                vec.z = skinWeight.getZ(i)
                vec.w = skinWeight.getW(i)

                scale = 1.0 / vec.manhattanLength()

                if scale != float("+inf"):
                    vec.multiplyScalar(scale)

                else:
                    vec.set(1, 0, 0, 0)     # do something reasonable

                skinWeight.setXYZW(i, vec.x, vec.y, vec.z, vec.w)

    def updateMatrixWorld(self, force=False, parent_matrixWorld_is_updated=True):
        super().updateMatrixWorld(force, parent_matrixWorld_is_updated)

        if self.bindMode == 'attached':
            self.bindMatrixInverse.getInverse(self.matrixWorld)

        elif self.bindMode == 'detached':
            self.bindMatrixInverse.getInverse(self.bindMatrix)

        else:
            print('THREE.SkinnedMesh: Unrecognized bindMode: ' + self.bindMode)

    def clone(self):
        return type(self)(self.geometry, self.material ).copy(self)
