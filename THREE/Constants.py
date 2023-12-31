import math
import time


class _number:
    def __init__(self):
        self.EPSILON = math.pow( 2, - 52 )


class Profiler:
    def __init__(self):
        self.t0 = 0
        self.times = []
        self.total = 0
        self.count = 0
        self.run = False
        self.names = {}

    def  start(self, name=None):
        if name:
            if name not in self.names:
                self.names[name] = [0, 0, 0]
            self.names[name][0] = time.time()

        else:
            self.t0 = time.clock()

    def stop(self, name=None):
        t1 = time.time()
        if name:
            p = self.names[name]
            p[1] += (t1 - p[0])
            p[2] += 1
        else:
            self.total += (t1 - self.t0)
            self.count += 1

    def print(self):
        for name in self.names.keys():
            p = self.names[name]
            avg = p[1] / p[2]
            print("%s %.15f %f %d" % (name, avg, p[1], p[2]))


profiler = Profiler()

Number = _number()

REVISION = '95'
MOUSE = { 'LEFT': 0, 'MIDDLE': 1, 'RIGHT': 2 }
CullFaceNone = 0
CullFaceBack = 1
CullFaceFront = 2
CullFaceFrontBack = 3
FrontFaceDirectionCW = 0
FrontFaceDirectionCCW = 1
BasicShadowMap = 0
PCFShadowMap = 1
PCFSoftShadowMap = 2
FrontSide = 0
BackSide = 1
DoubleSide = 2
FlatShading = 1
SmoothShading = 2
NoColors = 0
FaceColors = 1
VertexColors = 2
NoBlending = 0
NormalBlending = 1
AdditiveBlending = 2
SubtractiveBlending = 3
MultiplyBlending = 4
CustomBlending = 5
AddEquation = 100
SubtractEquation = 101
ReverseSubtractEquation = 102
MinEquation = 103
MaxEquation = 104
ZeroFactor = 200
OneFactor = 201
SrcColorFactor = 202
OneMinusSrcColorFactor = 203
SrcAlphaFactor = 204
OneMinusSrcAlphaFactor = 205
DstAlphaFactor = 206
OneMinusDstAlphaFactor = 207
DstColorFactor = 208
OneMinusDstColorFactor = 209
SrcAlphaSaturateFactor = 210
NeverDepth = 0
AlwaysDepth = 1
LessDepth = 2
LessEqualDepth = 3
EqualDepth = 4
GreaterEqualDepth = 5
GreaterDepth = 6
NotEqualDepth = 7
MultiplyOperation = 0
MixOperation = 1
AddOperation = 2
NoToneMapping = 0
LinearToneMapping = 1
ReinhardToneMapping = 2
Uncharted2ToneMapping = 3
CineonToneMapping = 4
UVMapping = 300
CubeReflectionMapping = 301
CubeRefractionMapping = 302
EquirectangularReflectionMapping = 303
EquirectangularRefractionMapping = 304
SphericalReflectionMapping = 305
CubeUVReflectionMapping = 306
CubeUVRefractionMapping = 307
RepeatWrapping = 1000
ClampToEdgeWrapping = 1001
MirroredRepeatWrapping = 1002
NearestFilter = 1003
NearestMipMapNearestFilter = 1004
NearestMipMapLinearFilter = 1005
LinearFilter = 1006
LinearMipMapNearestFilter = 1007
LinearMipMapLinearFilter = 1008
UnsignedByteType = 1009
ByteType = 1010
ShortType = 1011
UnsignedShortType = 1012
IntType = 1013
UnsignedIntType = 1014
FloatType = 1015
HalfFloatType = 1016
UnsignedShort4444Type = 1017
UnsignedShort5551Type = 1018
UnsignedShort565Type = 1019
UnsignedInt248Type = 1020
AlphaFormat = 1021
RGBFormat = 1022
RGBAFormat = 1023
RGBA32Format = 4023
LuminanceFormat = 1024
LuminanceAlphaFormat = 1025
RGBEFormat = RGBAFormat
DepthFormat = 1026
DepthStencilFormat = 1027
RGB_S3TC_DXT1_Format = 33776
RGBA_S3TC_DXT1_Format = 33777
RGBA_S3TC_DXT3_Format = 33778
RGBA_S3TC_DXT5_Format = 33779
RGB_PVRTC_4BPPV1_Format = 35840
RGB_PVRTC_2BPPV1_Format = 35841
RGBA_PVRTC_4BPPV1_Format = 35842
RGBA_PVRTC_2BPPV1_Format = 35843
RGB_ETC1_Format = 36196
RGBA_ASTC_4x4_Format = 37808
RGBA_ASTC_5x4_Format = 37809
RGBA_ASTC_5x5_Format = 37810
RGBA_ASTC_6x5_Format = 37811
RGBA_ASTC_6x6_Format = 37812
RGBA_ASTC_8x5_Format = 37813
RGBA_ASTC_8x6_Format = 37814
RGBA_ASTC_8x8_Format = 37815
RGBA_ASTC_10x5_Format = 37816
RGBA_ASTC_10x6_Format = 37817
RGBA_ASTC_10x8_Format = 37818
RGBA_ASTC_10x10_Format = 37819
RGBA_ASTC_12x10_Format = 37820
RGBA_ASTC_12x12_Format = 37821
LoopOnce = 2200
LoopRepeat = 2201
LoopPingPong = 2202
InterpolateDiscrete = 2300
InterpolateLinear = 2301
InterpolateSmooth = 2302
ZeroCurvatureEnding = 2400
ZeroSlopeEnding = 2401
WrapAroundEnding = 2402
TrianglesDrawMode = 0
TriangleStripDrawMode = 1
TriangleFanDrawMode = 2
LinearEncoding = 3000
sRGBEncoding = 3001
GammaEncoding = 3007
RGBEEncoding = 3002
LogLuvEncoding = 3003
RGBM7Encoding = 3004
RGBM16Encoding = 3005
RGBDEncoding = 3006
BasicDepthPacking = 3200
RGBADepthPacking = 3201
TangentSpaceNormalMap = 0
ObjectSpaceNormalMap = 1