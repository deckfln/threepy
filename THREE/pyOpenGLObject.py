"""
placeholder to simulate javascript feature like "isObject"
"""
from numba import *
import numpy as np

isColor = 1
isMatrix3 = 2
isMatrix4 = 4
isVector2 = 8
isVector3 = 16
isLight = 32
isSprite = 64
isLensFlare = 128
isImmediateRenderObject = 256
isLine = 512
isPoints = 1024
isSkinnedMesh = 2048
isGeometry = 4096
isInterleavedBufferAttribute = 8192
isBufferGeometry = 16384
isAmbientLight = 32768
isCubeTexture = 65536
isTexture = 131072
isArrayCamera = 262144
isRawShaderMaterial = 524288
isShaderMaterial = 1048576
isMeshPhongMaterial = 2097152
isMeshStandardMaterial = 4194304
isMeshBasicMaterial = 8388608
isInstancedBufferGeometry = 16777216
isInstancedBufferAttribute = 33554432
isMeshLambertMaterial = 67108864
isWebGLRenderTarget = 134217728
isDepthTexture = 268435456
isCompressedTexture = 536870912
isMeshNormalMaterial = 1073741824
isMeshDepthMaterial = 2147483648
isMeshDistanceMaterial = 4294967296
isLineDashedMaterial = 8589934592
isLineSegments = 17179869184
isLineLoop = 34359738368
isMeshToonMaterial = 68719476736
isLineBasicMaterial = 137438953472
isPointsMaterial = 274877906944
isShadowMaterial = 549755813888
isCamera = 1099511627776
isDirectionalLight = 2199023255552
isSpotLight = 4398046511104
isRectAreaLight = 8796093022208
isPointLight = 17592186044416
isWebGLRenderTargetCube = 35184372088832
isSpotLightShadow = 70368744177664
isFog = 140737488355328
isFogExp2 = 281474976710656
isEllipseCurve = 562949953421312
isVector4 = 1125899906842624
isMaterial = 2251799813685248
isMesh = 4503599627370496
isMeshPhysicalMaterial = 9007199254740992
isObject3D = 18014398509481984
isLineCurve = 36028797018963968
isHemisphereLight = 72057594037927936


class pyOpenGLObject:
    """
    profiler shows that dynamic "is" is slowwww
    def __getattr__(self, item):
        if item[:2] == "is":
            return item in self.__dict__

        raise AttributeError("Missing attribute %s" % item)
    """

    def __init__(self):
        self._onDispose = None
        self.class_code = 0

    def addEventListener(self, event, func):
        self._onDispose = func

    def is_a(self, kind):
        return hasattr(self, "is"+kind)

    def set_class(self, flag):
        self.class_code |= flag

    def my_class(self, flag):
        return self.class_code & flag
