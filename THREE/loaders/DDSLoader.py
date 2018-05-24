"""
 * @author mrdoob / http:#mrdoob.com/
"""
import numpy as np

from THREE.Constants import *
from THREE.CompressedTextureLoader import *
from THREE.javascriparray import *


class DDSLoader(CompressedTextureLoader):
    def __init__(self):
        self._parser = self.parse
        self.manager = None
        self.path = None

    def parse(self, buffer, loadMipmaps ):
        dds = { 'mipmaps': [], 'width': 0, 'height': 0, 'format': None, 'mipmapCount': 1 }

        # Adapted from @toji's DDS utils
        # https:#github.com/toji/webgl-texture-utils/blob/master/texture-util/dds.js

        # All values and structures referenced from:
        # http:#msdn.microsoft.com/en-us/library/bb943991.aspx/

        DDS_MAGIC = 0x20534444

        DDSD_CAPS = 0x1
        DDSD_HEIGHT = 0x2
        DDSD_WIDTH = 0x4
        DDSD_PITCH = 0x8
        DDSD_PIXELFORMAT = 0x1000
        DDSD_MIPMAPCOUNT = 0x20000
        DDSD_LINEARSIZE = 0x80000
        DDSD_DEPTH = 0x800000

        DDSCAPS_COMPLEX = 0x8
        DDSCAPS_MIPMAP = 0x400000
        DDSCAPS_TEXTURE = 0x1000

        DDSCAPS2_CUBEMAP = 0x200
        DDSCAPS2_CUBEMAP_POSITIVEX = 0x400
        DDSCAPS2_CUBEMAP_NEGATIVEX = 0x800
        DDSCAPS2_CUBEMAP_POSITIVEY = 0x1000
        DDSCAPS2_CUBEMAP_NEGATIVEY = 0x2000
        DDSCAPS2_CUBEMAP_POSITIVEZ = 0x4000
        DDSCAPS2_CUBEMAP_NEGATIVEZ = 0x8000
        DDSCAPS2_VOLUME = 0x200000

        DDPF_ALPHAPIXELS = 0x1
        DDPF_ALPHA = 0x2
        DDPF_FOURCC = 0x4
        DDPF_RGB = 0x40
        DDPF_YUV = 0x200
        DDPF_LUMINANCE = 0x20000

        def fourCCToInt32( value ):
            return ord(value[0]) + \
                ( ord(value[1]) << 8 ) + \
                ( ord(value[2]) << 16 ) + \
                ( ord(value[3]) << 24 )

        def int32ToFourCC( value ):
            return chr(value & 0xff) + \
                chr(( value >> 8 ) & 0xff) + \
                chr(( value >> 16 ) & 0xff) + \
                chr(( value >> 24 ) & 0xff)

        def loadARGBMip( buffer, dataOffset, width, height ):
            dt = np.dtype(np.uint8)
            dataLength = width * height * 4
            srcBuffer= np.frombuffer(buffer, dt, dataLength, dataOffset)
            byteArray = Uint8Array( dataLength )
            dst = 0
            src = 0
            for y in range(height):
                for x in range(width):
                    b = srcBuffer[ src ]
                    g = srcBuffer[ src + 1]
                    r = srcBuffer[ src + 2]
                    a = srcBuffer[ src + 3]
                    src += 4
                    
                    byteArray[ dst ] = r    #r
                    byteArray[ dst + 1] = g     #g
                    byteArray[ dst + 2] = b     #b
                    byteArray[ dst + 3] = a     #a
                    dst += 4

            return byteArray

        FOURCC_DXT1 = fourCCToInt32( "DXT1" )
        FOURCC_DXT3 = fourCCToInt32( "DXT3" )
        FOURCC_DXT5 = fourCCToInt32( "DXT5" )
        FOURCC_ETC1 = fourCCToInt32( "ETC1" )

        headerLengthInt = 31     # The header length in 32 bit ints

        # Offsets into the header array

        off_magic = 0

        off_size = 1
        off_flags = 2
        off_height = 3
        off_width = 4

        off_mipmapCount = 7

        off_pfFlags = 20
        off_pfFourCC = 21
        off_RGBBitCount = 22
        off_RBitMask = 23
        off_GBitMask = 24
        off_BBitMask = 25
        off_ABitMask = 26

        off_caps = 27
        off_caps2 = 28
        off_caps3 = 29
        off_caps4 = 30

        # Parse header

        dt = np.int32
        header = np.frombuffer(buffer, dt, headerLengthInt, 0)

        if header[ off_magic ] != DDS_MAGIC:
            raise RuntimeError( 'THREE.DDSLoader.parse: Invalid magic number in DDS header.' )

        if not header[ off_pfFlags ] & DDPF_FOURCC: 
            raise RuntimeError( 'THREE.DDSLoader.parse: Unsupported format, must contain a FourCC code.' )

        fourCC = header[ off_pfFourCC ]

        isRGBAUncompressed = False

        if fourCC == FOURCC_DXT1:
            blockBytes = 8
            dds['format'] = RGB_S3TC_DXT1_Format

        elif fourCC == FOURCC_DXT3:
            blockBytes = 16
            dds['format'] = RGBA_S3TC_DXT3_Format

        elif fourCC == FOURCC_DXT5:
            blockBytes = 16
            dds['format'] = RGBA_S3TC_DXT5_Format

        elif fourCC == FOURCC_ETC1:
            blockBytes = 8
            dds['format'] = RGB_ETC1_Format

        else:
                if header[ off_RGBBitCount ] == 32 \
                    and (header[ off_RBitMask ] & 0xff0000) \
                    and (header[ off_GBitMask ] & 0xff00) \
                    and (header[ off_BBitMask ] & 0xff) \
                    and (header[ off_ABitMask ] & 0xff000000):

                    isRGBAUncompressed = True
                    blockBytes = 64
                    dds['format'] = RGBAFormat
                else:
                    raise RuntimeError( 'THREE.DDSLoader.parse: Unsupported FourCC code ', int32ToFourCC( fourCC ) )

        dds['mipmapCount'] = 1

        if (header[ off_flags ] & DDSD_MIPMAPCOUNT) and loadMipmaps != False:
            dds['mipmapCount'] = max( 1, header[ off_mipmapCount ] )

        caps2 = header[ off_caps2 ]
        dds['isCubemap'] = True if caps2 & DDSCAPS2_CUBEMAP else False
        if dds['isCubemap'] and (
            not ( caps2 & DDSCAPS2_CUBEMAP_POSITIVEX ) or
            not ( caps2 & DDSCAPS2_CUBEMAP_NEGATIVEX ) or
            not ( caps2 & DDSCAPS2_CUBEMAP_POSITIVEY ) or
            not ( caps2 & DDSCAPS2_CUBEMAP_NEGATIVEY ) or
            not ( caps2 & DDSCAPS2_CUBEMAP_POSITIVEZ ) or
            not ( caps2 & DDSCAPS2_CUBEMAP_NEGATIVEZ )
            ):
            raise RuntimeError( 'THREE.DDSLoader.parse: Incomplete cubemap faces' )

        dds['width'] = header[ off_width ]
        dds['height'] = header[ off_height ]

        dataOffset = header[ off_size ] + 4

        # Extract mipmaps buffers

        faces = 6 if dds['isCubemap'] else 1

        dt = np.dtype(np.uint8)
        ba = np.fromstring(buffer, dt)

        for face in range(faces):
            width = dds['width']
            height = dds['height']

            for i in range(dds['mipmapCount']):
                if isRGBAUncompressed:
                    byteArray = loadARGBMip( buffer, dataOffset, width, height )
                    dataLength = byteArray.length

                else:
                    dataLength = int(max( 4, width ) / 4 * max( 4, height ) / 4 * blockBytes)
                    byteArray = ba[dataOffset:dataOffset+dataLength]

                mipmap = MipMap(width, height, byteArray)
                dds['mipmaps'].append( mipmap )

                dataOffset += dataLength

                width = max( width >> 1, 1 )
                height = max( height >> 1, 1 )

        return dds
