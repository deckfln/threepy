"""
placeholder to simulate javascript feature like "isObject"
"""
from numba import *


class pyOpenGLObject:
    isMesh = False
    isColor = False
    isMatrix3 = False
    isMatrix4 = False
    isVector2 = False
    isVector3 = False
    isLight = False
    isSprite = False
    isLensFlare = False
    isImmediateRenderObject = False
    isLine = False
    isPoints = False
    isSkinnedMesh = False
    isGeometry = False
    isInterleavedBufferAttribute = False
    isBufferGeometry = False
    isAmbientLight = False
    isCubeTexture = False
    isTexture = False
    isArrayCamera = False
    isRawShaderMaterial = False
    isShaderMaterial = False
    isMeshPhongMaterial = False
    isMeshStandardMaterial = False
    isMeshBasicMaterial = False
    isInstancedBufferGeometry = False
    isInstancedBufferAttribute = False
    isMeshLambertMaterial = False
    isWebGLRenderTarget = False
    isDepthTexture = False
    isDataTexture = False
    isCompressedTexture = False
    isMeshNormalMaterial = False
    isMeshDepthMaterial = False
    isMeshDistanceMaterial = False
    isLineDashedMaterial = False
    isLineSegments = False
    isLineLoop = False
    """
    profiler shows that dynamic "is" is slowwww
    def __getattr__(self, item):
        if item[:2] == "is":
            return item in self.__dict__

        raise AttributeError("Missing attribute %s" % item)
    """