"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from OpenGL.GL import *

from THREE.Constants import *


class pyOpenGLExtensions():
    def __init__(self):
        self.extensions = {}
        self.s = (glGetString(GL_EXTENSIONS)).decode("utf-8")

    def get(self, name):
        if name in self.extensions: 
            return self.extensions[ name ]

        self.extensions[name] = name in self.s

        return self.extensions[name]
        

"""
/**
 * @author thespite / http://www.twitter.com/thespite
 */
"""


class pyOpenGLUtils():
    def __init__(self, extensions):
        self.extensions = extensions
        self.map = {
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
            SrcAlphaSaturateFactor: GL_SRC_ALPHA_SATURATE
        }

    def convert(self, p):
        if p in self.map:
            return self.map[p]

        if p == HalfFloatType:
            extension = self.extensions.get( 'OES_texture_half_float' )
            if extension is not None:
                return 0x8D61  # // HALF_FLOAT_OES

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

        if p == RGB_ETC1_Format:
            extension = self.extensions.get( 'compressed_texture_etc1' )
            if extension:
                return 0x8D64C  # // COMPRESSED_RGB_ETC1_WEBGL

        if p == MinEquation or p == MaxEquation:
            extension = self.extensions.get( 'EXT_blend_minmax' )
            if extension:
                if p == MinEquation:
                    return 0x8007  # // MIN_EXT
                if p == MaxEquation:
                    return 0x8008   # // MAX_EXT

        if p == UnsignedInt248Type:
            extension = self.extensions.get( 'depth_texture' )
            if extension:
                return GL_DEPTH24_STENCIL8

        return 0
