"""
/**
 * @author thespite / http://www.twitter.com/thespite
 */
"""

from THREE.Constants import *
from OpenGL.GL import *


_map = {
    RepeatWrapping: GL_REPEAT,
    ClampToEdgeWrapping: GL_CLAMP_TO_EDGE,
    MirroredRepeatWrapping: GL_MIRRORED_REPEAT,
    NearestFilter: GL_NEAREST,
    NearestMipMapNearestFilter: GL_NEAREST_MIPMAP_NEAREST,
    NearestMipMapLinearFilter: GL_NEAREST_MIPMAP_LINEAR,
    LinearFilter: GL_LINEAR,
    LinearMipMapNearestFilter: GL_LINEAR_MIPMAP_NEAREST,
    LinearMipMapLinearFilter: GL_LINEAR_MIPMAP_LINEAR,
    UnsignedByteType: GL_UNSIGNED_BYTE,
    UnsignedShort4444Type: GL_UNSIGNED_SHORT_4_4_4_4,
    UnsignedShort5551Type: GL_UNSIGNED_SHORT_5_5_5_1,
    UnsignedShort565Type: GL_UNSIGNED_SHORT_5_6_5,
    ByteType: GL_BYTE,
    ShortType: GL_SHORT,
    UnsignedShortType: GL_UNSIGNED_SHORT,
    IntType: GL_INT,
    UnsignedIntType: GL_UNSIGNED_INT,
    FloatType: GL_FLOAT,
    AlphaFormat: GL_ALPHA,
    RGBFormat: GL_RGB,
    RGBAFormat: GL_RGBA,
    RGBA32Format: GL_RGBA32F,
    LuminanceFormat: GL_LUMINANCE,
    LuminanceAlphaFormat: GL_LUMINANCE_ALPHA,
    DepthFormat: GL_DEPTH_COMPONENT,
    DepthStencilFormat: GL_DEPTH_STENCIL,
    AddEquation: GL_FUNC_ADD,
    SubtractEquation: GL_FUNC_SUBTRACT,
    ReverseSubtractEquation: GL_FUNC_REVERSE_SUBTRACT,
    ZeroFactor: GL_ZERO,
    OneFactor: GL_ONE,
    SrcColorFactor: GL_SRC_COLOR,
    OneMinusSrcColorFactor: GL_ONE_MINUS_SRC_COLOR,
    SrcAlphaFactor: GL_SRC_ALPHA,
    OneMinusSrcAlphaFactor: GL_ONE_MINUS_SRC_ALPHA,
    DstAlphaFactor: GL_DST_ALPHA,
    OneMinusDstAlphaFactor: GL_ONE_MINUS_DST_ALPHA,
    DstColorFactor: GL_DST_COLOR,
    OneMinusDstColorFactor: GL_ONE_MINUS_DST_COLOR,
    SrcAlphaSaturateFactor: GL_SRC_ALPHA_SATURATE,
    HalfFloatType: GL_HALF_FLOAT,
    MinEquation: GL_MIN,
    MaxEquation: GL_MAX,
    UnsignedInt248Type: GL_UNSIGNED_INT_24_8
}


class pyOpenGLUtils():
    def __init__(self, extensions):
        self.extensions = extensions

    def convert(self, p):
        if p in _map:
            return _map[p]

        if p == RGB_S3TC_DXT1_Format or p == RGBA_S3TC_DXT1_Format or \
            p == RGBA_S3TC_DXT3_Format or p == RGBA_S3TC_DXT5_Format:

            extension = self.extensions.get( 'texture_compression_s3tc')  # compressed_texture_s3tc' )
            if extension:
                if p == RGB_S3TC_DXT1_Format:
                    return 0x83F0  # // COMPRESSED_RGB_S3TC_DXT1_EXT
                if p == RGBA_S3TC_DXT1_Format:
                    return 0x83F1  # // COMPRESSED_RGBA_S3TC_DXT1_EXT
                if p == RGBA_S3TC_DXT3_Format:
                    return 0x83F2  # // COMPRESSED_RGBA_S3TC_DXT3_EXT
                if p == RGBA_S3TC_DXT5_Format:
                    return 0x83F3  # // COMPRESSED_RGBA_S3TC_DXT5_EXT

        if p == RGB_PVRTC_4BPPV1_Format or p == RGB_PVRTC_2BPPV1_Format or \
            p == RGBA_PVRTC_4BPPV1_Format or p == RGBA_PVRTC_2BPPV1_Format:

            extension = self.extensions.get( 'compressed_texture_pvrtc' )

            if extension:
                if p == RGB_PVRTC_4BPPV1_Format:
                    return 0x8C00  # // COMPRESSED_RGB_PVRTC_4BPPV1_IMG
                if p == RGB_PVRTC_2BPPV1_Format:
                    return 0x8C01  # // COMPRESSED_RGB_PVRTC_2BPPV1_IMG
                if p == RGBA_PVRTC_4BPPV1_Format:
                    return 0x8C02  # // COMPRESSED_RGBA_PVRTC_4BPPV1_IMG
                if p == RGBA_PVRTC_2BPPV1_Format:
                    return 0x8C03  # // COMPRESSED_RGBA_PVRTC_2BPPV1_IMG

        if p == RGBA_ASTC_4x4_Format or p == RGBA_ASTC_5x4_Format or p == RGBA_ASTC_5x5_Format or \
            p == RGBA_ASTC_6x5_Format or p == RGBA_ASTC_6x6_Format or p == RGBA_ASTC_8x5_Format or \
            p == RGBA_ASTC_8x6_Format or p == RGBA_ASTC_8x8_Format or p == RGBA_ASTC_10x5_Format or \
            p == RGBA_ASTC_10x6_Format or p == RGBA_ASTC_10x8_Format or p == RGBA_ASTC_10x10_Format or \
            p == RGBA_ASTC_12x10_Format or p == RGBA_ASTC_12x12_Format:

            extension = self.extensions.get( 'WEBGL_compressed_texture_astc' )

            if extension is not None:
                return p

        if p == RGB_ETC1_Format:
            extension = self.extensions.get( 'compressed_texture_etc1' )
            if extension:
                return 0x8D64C  # // COMPRESSED_RGB_ETC1_WEBGL

        return 0
