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

    def getWorldDirection(self, optionalTarget=None):
        quaternion = Quaternion()
        result = optionalTarget or Vector3()

        self.getWorldQuaternion(quaternion)

        return result.set(0, 0, - 1).applyQuaternion(quaternion)

    def updateMatrixWorld(self, force=False):
        super().updateMatrixWorld(force)

        self.matrixWorldInverse.updated = False
        if self.matrixWorld.updated:
            self.matrixWorldInverse.getInverse(self.matrixWorld)
            self.matrixWorldInverse.updated = True

    def clone(self, recursive=True):
        return type(self)().copy(self, recursive)


"""
    /**
     * @author alteredq / http://alteredqualia.com/
     * @author arose / http://github.com/arose
     */
"""


class _View:
    def __init__(self, fullWidth, fullHeight, x, y, width, height):
        self.fullWidth = fullWidth
        self.fullHeight = fullHeight
        self.offsetX = x
        self.offsetY = y
        self.width = width
        self.height = height

        
class OrthographicCamera(Camera):
    isOrthographicCamera = True
        
    def __init__(self, left, right, top, bottom, near=0.1, far=2000):
        super().__init__()

        self.type = 'OrthographicCamera'

        self.zoom = 1
        self.view = None

        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

        self.near = near
        self.far = far

        self.updateProjectionMatrix()

    def copy(self, source, recursive=True):
        super().copy(source, recursive)

        self.left = source.left
        self.right = source.right
        self.top = source.top
        self.bottom = source.bottom
        self.near = source.near
        self.far = source.far

        self.zoom = source.zoom
        self.view = None
        if source.view is not None :
            self.view = source.view
        
        return self

    def setViewOffset(self, fullWidth, fullHeight, x, y, width, height):
        self.view = _View(fullWidth, fullHeight, x, y, width, height)
        self.updateProjectionMatrix()

    def clearViewOffset(self):
        self.view = None
        self.updateProjectionMatrix()

    def updateProjectionMatrix(self):
        dx = (self.right - self.left) / (2 * self.zoom)
        dy = (self.top - self.bottom) / (2 * self.zoom)
        cx = (self.right + self.left) / 2
        cy = (self.top + self.bottom) / 2

        left = cx - dx
        right = cx + dx
        top = cy + dy
        bottom = cy - dy

        if self.view is not None:
            zoomW = self.zoom / (self.view.width / self.view.fullWidth)
            zoomH = self.zoom / (self.view.height / self.view.fullHeight)
            scaleW = (self.right - self.left) / self.view.width
            scaleH = (self.top - self.bottom) / self.view.height

            left += scaleW * (self.view.offsetX / zoomW)
            right = left + scaleW * (self.view.width / zoomW)
            top -= scaleH * (self.view.offsetY / zoomH)
            bottom = top - scaleH * (self.view.height / zoomH)

        self.projectionMatrix.makeOrthographic(left, right, top, bottom, self.near, self.far)

        return self.projectionMatrix.is_updated()

    def toJSON(self, meta):
        data = super().toJSON(meta)

        data.object.zoom = self.zoom
        data.object.left = self.left
        data.object.right = self.right
        data.object.top = self.top
        data.object.bottom = self.bottom
        data.object.near = self.near
        data.object.far = self.far

        if self.view is not None:
            data.object.view = self.view

        return data

"""        
    /**
     * @author mrdoob / http://mrdoob.com/
     * @author greggman / http://games.greggman.com/
     * @author zz85 / http://www.lab4games.net/zz85/blog
     * @author tschw
     */
"""


class PerspectiveCamera(Camera):
    isPerspectiveCamera = True
        
    def __init__(self, fov=50, aspect=1, near=0.1, far=2000):
        super().__init__()
        self.type = 'PerspectiveCamera'

        self.fov = fov
        self.zoom = 1

        self.near = near
        self.far = far
        self.focus = 10

        self.aspect = aspect
        self.view = None

        self.filmGauge = 35    # // width of the film (default in millimeters)
        self.filmOffset = 0    # // horizontal film offset (same unit as gauge)

        self.updateProjectionMatrix()

    def copy(self, source, recursive=True):
        super().copy(source, recursive)

        self.fov = source.fov
        self.zoom = source.zoom

        self.near = source.near
        self.far = source.far
        self.focus = source.focus

        self.aspect = source.aspect
        self.view = None
        if source.view is not None:
            self.view = source.view
            
        self.filmGauge = source.filmGauge
        self.filmOffset = source.filmOffset

        return self

    def setFocalLength(self, focalLength):
        """
        /**
         * Sets the FOV by focal length in respect to the current .filmGauge.
         *
         * The default film gauge is 35, so that the focal length can be specified for
         * a 35mm (full frame) camera.
         *
         * Values for focal length and film gauge must have the same unit.
         */
        """
        
        # // see http://www.bobatkins.com/photography/technical/field_of_view.html
        vExtentSlope = 0.5 * self.getFilmHeight() / focalLength

        self.fov = _Math.RAD2DEG * 2 * math.atan(vExtentSlope)
        self.updateProjectionMatrix()

    def getFocalLength(self):
        """
        /**
        * Calculates the focal length from the current .fov and .filmGauge.
        */
        """
        vExtentSlope = math.tan(_Math.DEG2RAD * 0.5 * self.fov)

        return 0.5 * self.getFilmHeight() / vExtentSlope

    def getEffectiveFOV(self):
            return _Math.RAD2DEG * 2 * math.atan(
                    math.tan(_Math.DEG2RAD * 0.5 * self.fov) / self.zoom)

    def getFilmWidth(self):
        # // film not completely covered in portrait format (aspect < 1)
        return self.filmGauge * min(self.aspect, 1)

    def getFilmHeight(self):
        # // film not completely covered in landscape format (aspect > 1)
        return self.filmGauge / max(self.aspect, 1)

    def setViewOffset(self, fullWidth, fullHeight, x, y, width, height):
        """
        /**
         * Sets an offset in a larger frustum. This is useful for multi-window or
         * multi-monitor/multi-machine setups.
         *
         * For example, if you have 3x2 monitors and each monitor is 1920x1080 and
         * the monitors are in grid like self
         *
         *   +---+---+---+
         *   | A | B | C |
         *   +---+---+---+
         *   | D | E | F |
         *   +---+---+---+
         *
         * then for each monitor you would call it like self
         *
         *   w = 1920
         *   h = 1080
         *   fullWidth = w * 3
         *   fullHeight = h * 2
         *
         *   --A--
         *   camera.setOffset(fullWidth, fullHeight, w * 0, h * 0, w, h)
         *   --B--
         *   camera.setOffset(fullWidth, fullHeight, w * 1, h * 0, w, h)
         *   --C--
         *   camera.setOffset(fullWidth, fullHeight, w * 2, h * 0, w, h)
         *   --D--
         *   camera.setOffset(fullWidth, fullHeight, w * 0, h * 1, w, h)
         *   --E--
         *   camera.setOffset(fullWidth, fullHeight, w * 1, h * 1, w, h)
         *   --F--
         *   camera.setOffset(fullWidth, fullHeight, w * 2, h * 1, w, h)
         *
         *   Note there is no reason monitors have to be the same size or in a grid.
         */        
        """
        self.aspect = fullWidth / fullHeight

        self.view = _View(fullWidth,fullHeight, x, y, width, height)

        self.updateProjectionMatrix()

    def clearViewOffset(self):
        self.view = None
        self.updateProjectionMatrix()

    def updateProjectionMatrix(self):
        near = self.near
        top = near * math.tan(_Math.DEG2RAD * 0.5 * self.fov) / self.zoom
        height = 2 * top
        width = self.aspect * height
        left = - 0.5 * width
        view = self.view

        if view is not None:
            fullWidth = view.fullWidth
            fullHeight = view.fullHeight

            left += view.offsetX * width / fullWidth
            top -= view.offsetY * height / fullHeight
            width *= view.width / fullWidth
            height *= view.height / fullHeight

        skew = self.filmOffset
        if skew != 0:
            left += near * skew / self.getFilmWidth()

        self.projectionMatrix.makePerspective(left, left + width, top, top - height, near, self.far)

        return self.projectionMatrix.is_updated()

    def toJSON(self, meta):
        data = super().toJSON(meta)

        data.object.fov = self.fov
        data.object.zoom = self.zoom

        data.object.near = self.near
        data.object.far = self.far
        data.object.focus = self.focus

        data.object.aspect = self.aspect

        if self.view is not None: 
            data.object.view = self.view

        data.object.filmGauge = self.filmGauge
        data.object.filmOffset = self.filmOffset

        return data
