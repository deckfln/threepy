"""

"""
from THREE.objects.Group import *
from THREE.math.Sphere import *
import THREE.MeshUtils as MeshUtils


class OcTree(Group):
    def __init__(self, position, size):
        super().__init__()
        self.type = 'octree'

        self.set_class(isOctree)
        self.position = position
        self.size = size
        self.boundingSphere = Sphere(position, math.sqrt(3 * size * size))

        #mesh = THREE.Mesh(
        #    THREE.SphereBufferGeometry(self.boundingSphere.radius, 32,  32),
        #    THREE.MeshBasicMaterial({'color': self.size * 512, 'wireframe': True})
        #)
        #mesh.position = self.boundingSphere.center

        self.leaf = (size == 16)
        if not self.leaf:
            self.children = [None for i in range(8)]

        #if size < 256:
        #    self.children.append(mesh)

    def add(self, obj):
        if self.leaf:
            self.children.append(obj)
            return
        else:
            px = 0 if obj.position.x < self.position.x else 1
            py = 0 if obj.position.y < self.position.y else 1
            pz = 0 if obj.position.z < self.position.z else 1

            p = int(px + py * 2 + pz * 4)
            child = self.children[p]
            if child is None:
                if px == 0:
                    px = -1
                if py == 0:
                    py = -1
                if pz == 0:
                    pz = -1

                center = THREE.Vector3(
                    self.position.x + px * self.size/2,
                    self.position.y + py * self.size/2,
                    self.position.z + pz * self.size/2)

                self.children[p] = child = OcTree(center, self.size / 2)

            child.add(obj)

    def test(self):
        for child in self.children:
            if child is None:
                continue

            d = child.position.distanceTo(self.boundingSphere.center)
            if d > self.boundingSphere.radius:
                print("not good")

            if child.my_class(isOctree):
                child.test()

    def merge(self):
        if self.leaf:
            mesh = MeshUtils.mergeMeshes(self.children)
            self.children = [mesh]
        else:
            for child in self.children:
                if child is None:
                    continue

                child.merge()
