"""
    /**
     * @author mrdoob / http://mrdoob.com/
     * @author mikael emtinger / http://gomo.se/
     * @author WestLangley / http://github.com/WestLangley
    */
"""
import THREE._Math as _Math
from THREE.core.Object3D import *
from THREE.math.Quaternion import *


class CameraView:
    def __init__(self, enabled, fullWidth, fullHeight, offsetX, offsetY, width, height):
        self.enabled = enabled
        self.fullWidth = fullWidth
        self.fullHeight = fullHeight
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.width = width
        self.height = height


class Camera(Object3D):
    isCamera = True

    def __init__(self):
        super().__init__()
        self.set_class(isCamera)

        self.type = 'Camera'

        self.matrixWorldInverse = Matrix4()
        self.projectionMatrix = Matrix4()

    def copy(self, source, recursive=True):
        super().copy(source, recursive)
        self.matrixWorldInverse.copy(source.matrixWorldInverse)
        self.projectionMatrix.copy(source.projectionMatrix)
        return self

    def getWorldDirection(self, target):
        quaternion = Quaternion()

        self.getWorldQuaternion(quaternion)

        return target.set(0, 0, - 1).applyQuaternion(quaternion)

    def updateMatrixWorld(self, force=False, parent_matrixWorld_is_updated=True):
        super().updateMatrixWorld(force, parent_matrixWorld_is_updated)

        if self.matrixWorld.updated:
            self.matrixWorldInverse.getInverse(self.matrixWorld)

    def reset_update_flags(self):
        super().reset_update_flags()
        self.matrixWorldInverse.updated = False
        self.projectionMatrix.updated = False

    def clone(self, recursive=True):
        return type(self)().copy(self, recursive)
