"""
/ **
  * @ author alteredq / http: // alteredqualia.com
  * /
"""
from THREE.renderers.pyOpenGLRenderTarget import *


class pyOpenGLRenderTargetCube(pyOpenGLRenderTarget):
    isWebGLRenderTargetCube = True

    def __init__(self, width, height, options):
        super().__init__(width, height, options)

        self.activeCubeFace = 0 # // PX0, NX1, PY2, NY3, PZ4, NZ5
        self.activeMipMapLevel = 0

        self.set_class(isWebGLRenderTargetCube)
