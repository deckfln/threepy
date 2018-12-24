"""
    /**
     * @author alteredq / http://alteredqualia.com/
     * @author arose / http://github.com/arose
     */
"""
from THREE.cameras.Camera import *


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
        if source.view is not None:
            self.view = source.view

        return self

    def setViewOffset(self, fullWidth, fullHeight, x, y, width, height):
        if self.view is None:
            self.view = CameraView(True, 1, 1, 0, 0, 1, 1)

        self.view.enabled = True
        self.view.fullWidth = fullWidth
        self.view.fullHeight = fullHeight
        self.view.offsetX = x
        self.view.offsetY = y
        self.view.width = width
        self.view.height = height

        self.updateProjectionMatrix()

    def clearViewOffset(self):
        if self.view is not None:
            self.view.enabled = False

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

        if self.view is not None and self.view.enabled:
            zoomW = self.zoom / (self.view.width / self.view.fullWidth)
            zoomH = self.zoom / (self.view.height / self.view.fullHeight)
            scaleW = (self.right - self.left) / self.view.width
            scaleH = (self.top - self.bottom) / self.view.height

            left += scaleW * (self.view.offsetX / zoomW)
            right = left + scaleW * (self.view.width / zoomW)
            top -= scaleH * (self.view.offsetY / zoomH)
            bottom = top - scaleH * (self.view.height / zoomH)

        self.projectionMatrix.makeOrthographic(left, right, top, bottom, self.near, self.far)

        return self.projectionMatrix.updated

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

