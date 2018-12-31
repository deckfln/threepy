"""
 * @author alteredq / http://alteredqualia.com/
 * @author mrdoob / http://mrdoob.com/
 * @author WestLangley / http://github.com/WestLangley
"""

from THREE.math.Vector3 import *
from THREE.core.Object3D import *
from THREE.objects.Line import  *
from THREE.core.BufferAttribute import Float32BufferAttribute
from THREE.core.BufferGeometry import *
from THREE.materials.LineBasicMaterial import *


_v1 = Vector3()
_v2 = Vector3()
_v3 = Vector3()


class DirectionalLightHelper(Object3D):
    def __init__(self, light, size=1, color=None):
        super().__init__()

        self.light = light
        self.light.updateMatrixWorld()

        self.matrix = light.matrixWorld
        self.matrixAutoUpdate = False

        self.color = color

        geometry = BufferGeometry()
        geometry.addAttribute('position', Float32BufferAttribute([
            - size, size, 0,
            size, size, 0,
            size, - size, 0,
            - size, - size, 0,
            - size, size, 0
        ], 3))

        material = LineBasicMaterial({'fog': False})

        self.lightPlane = Line(geometry, material)
        self.add(self.lightPlane)

        geometry = BufferGeometry()
        geometry.addAttribute('position', Float32BufferAttribute([0, 0, 0, 0, 0, 1], 3))

        self.targetLine = Line(geometry, material)
        self.add(self.targetLine)

        self.update()

    def update(self):
        _v1.setFromMatrixPosition(self.light.matrixWorld)
        _v2.setFromMatrixPosition(self.light.target.matrixWorld)
        _v3.subVectors(_v2, _v1)

        self.lightPlane.lookAt(_v3)

        if self.color is not None:
            self.lightPlane.material.color.set(self.color)
            self.targetLine.material.color.set(self.color)

        else:
            self.lightPlane.material.color.copy(self.light.color)
            self.targetLine.material.color.copy(self.light.color)

        self.targetLine.lookAt(_v3)
        self.targetLine.scale.z = _v3.length()
