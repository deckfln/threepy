"""
placeholder to simulate javascript feature like "isObject"
"""
import numpy as np
from numpy import uintp

isColor = np.uint64(1)
isMatrix3 = np.uint64(2)
isMatrix4 = np.uint64(4)
isVector2 = np.uint64(8)
isVector3 = np.uint64(16)
isLight = np.uint64(32)
isSprite = np.uint64(64)
isLensFlare = np.uint64(128)
isImmediateRenderObject = np.uint64(256)
isLine = np.uint64(512)
isPoints = np.uint64(1024)
isSkinnedMesh = np.uint64(2048)
isGeometry = np.uint64(4096)
isInterleavedBufferAttribute = np.uint64(8192)
isBufferAttribute = np.uint64(16384)
isInterleavedBufferAttribute = np.uint64(32768)
isInstancedBufferAttribute = np.uint64(33554432)
isBufferGeometry = np.uint64(16384)
isInterleavedBuffer = np.uint64(65536)
isInstancedInterleavedBuffer = np.uint64(131072)
isAmbientLight = np.uint64(32768)

isTexture = np.uint64(32768)
isCubeTexture = np.uint64(65536)
isDataTexture = np.uint64(262144)
isDepthTexture = np.uint64(524288)
isDepthTexture = np.uint64(1048576)
isCompressedTexture = np.uint64(2097152)
isCanvasTexture = np.uint64(4194304)
isVideoTexture = np.uint64(8388608)
isTextureArray = np.uint64(16777216)
isDataTextureArray = np.uint64(33554432)

isFont = np.uint64(1048576)

isArrayCamera = np.uint64(262144)

isMaterial = np.uint64(2251799813685248)
isRawShaderMaterial = np.uint64(524288)
isShaderMaterial = np.uint64(1048576)
isMeshPhongMaterial = np.uint64(2097152)
isMeshStandardMaterial = np.uint64(4194304)
isMeshBasicMaterial = np.uint64(8388608)
isInstancedBufferGeometry = np.uint64(16777216)
isMeshLambertMaterial = np.uint64(67108864)
isWebGLRenderTarget = np.uint64(134217728)
isMeshNormalMaterial = np.uint64(1073741824)
isMeshDepthMaterial = np.uint64(2147483648)
isMeshDistanceMaterial = np.uint64(4294967296)
isLineDashedMaterial = np.uint64(8589934592)
isSpriteMaterial = np.uint64(17179869184)
isMeshToonMaterial = np.uint64(68719476736)
isLineBasicMaterial = np.uint64(137438953472)
isPointsMaterial = np.uint64(274877906944)
isShadowMaterial = np.uint64(549755813888)
isMeshPhysicalMaterial = np.uint64(9007199254740992)
isGLTFSpecularGlossinessMaterial = np.uint64(262144)

isGroup = np.uint64(72057594037927936)

isSplineCurve = np.uint64(8388608)
isEllipseCurve = np.uint64(16777216)
isLineCurve = np.uint64(67108864)
isLineCurve3 = np.uint64(134217728)

isLineSegments = np.uint64(17179869184)
isLineLoop = np.uint64(34359738368)

isCamera = np.uint64(1099511627776)
isPerspectiveCamera = np.uint64(2199023255552)
isOrthographicCamera = np.uint64(4398046511104)

isDirectionalLight = np.uint64(2199023255552)
isSpotLight = np.uint64(4398046511104)
isRectAreaLight = np.uint64(8796093022208)
isPointLight = np.uint64(17592186044416)
isWebGLRenderTargetCube = np.uint64(35184372088832)
isSpotLightShadow = np.uint64(70368744177664)
isFog = np.uint64(140737488355328)
isFogExp2 = np.uint64(281474976710656)
isVector4 = np.uint64(1125899906842624)
isMesh = np.uint64(4503599627370496)
isOctree = np.uint64(524288)
isObject3D = np.uint64(18014398509481984)
isHemisphereLight = np.uint64(72057594037927936)

isViewRenderer = np.uint64(0)
isShadowMapRenderer = np.uint64(1)
isCustomRenderer = np.uint64(2)


class pyOpenGLObject:
    """
    profiler shows that dynamic "is" is slowwww
    def __getattr__(self, item):
        if item[:2] == "is":
            return item in self.__dict__

        raise AttributeError("Missing attribute %s" % item)
    """
    class_code: np.uint64(0)

    def __init__(self):
        self._onDispose = None
        self.class_code = np.uint64(0)

    """
    def addEventListener(self, event, func):
        self._onDispose = func
    """

    def is_a(self, kind):
        return hasattr(self, "is"+kind)

    def set_class(self, flag):
        self.class_code |= flag

    def my_class(self, flag):
        return self.class_code & flag
