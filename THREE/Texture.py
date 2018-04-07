"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author alteredq / http:# //alteredqualia.com/
 * @author szimek / https:# //github.com/szimek/
 */
"""
import THREE._Math as _Math
from THREE.Constants import *
from THREE.pyOpenGLObject import *
from THREE.Vector2 import *


_textureId = 0


class Texture(pyOpenGLObject):
    DEFAULT_IMAGE = None
    DEFAULT_MAPPING = UVMapping
    isTexture = True
    
    def __init__(self, image=None, mapping=None, wrapS=None, wrapT=None, magFilter=None, minFilter=None, format=None, type=None, anisotropy=None, encoding=None ):
        global _textureId
        self.id = _textureId
        _textureId += 1

        super().__init__()
        self.set_class(isTexture)

        self.name = None
        self.uuid = _Math.generateUUID()

        self.name = ''

        self.image = image if image is not None else Texture.DEFAULT_IMAGE
        self.img_data = None
        self.mipmaps = []

        self.mapping = mapping if mapping is not None else Texture.DEFAULT_MAPPING

        self.wrapS = wrapS if wrapS is not None else ClampToEdgeWrapping
        self.wrapT = wrapT if wrapT is not None else ClampToEdgeWrapping

        self.magFilter = magFilter if magFilter is not None else LinearFilter
        self.minFilter = minFilter if minFilter is not None else LinearMipMapLinearFilter

        self.anisotropy = anisotropy if anisotropy is not None else 1

        self.format = format if format is not None else RGBAFormat
        self.type = type if type is not None else UnsignedByteType

        self.offset = Vector2( 0, 0 )
        self.repeat = Vector2( 1, 1 )

        self.generateMipmaps = True
        self.premultiplyAlpha = False
        self.flipY = True
        self.unpackAlignment = 4    # // valid values: 1, 2, 4, 8 (see http:# //www.khronos.org/opengles/sdk/docs/man/xhtml/glPixelStorei.xml)

        # // Values of encoding !== THREE.LinearEncoding only supported on map, envMap and emissiveMap.
        # //
        # // Also changing the encoding after already used by a Material will not automatically make the Material
        # // update.  You need to explicitly call Material.needsUpdate to trigger it to recompile.
        self.encoding = encoding if encoding is not None else LinearEncoding

        self.version = 0
        self.onUpdate = None
        self.callback = None

    def set(self, value ):
        if value:
            self.version += 1

    needsUpdate = property(None, set)
            
    def clone(self):
        return type(self)().copy( self )

    def copy(self, source ):
        self.name = source.name

        self.image = source.image
        self.mipmaps = source.mipmaps[:]

        self.mapping = source.mapping

        self.wrapS = source.wrapS
        self.wrapT = source.wrapT

        self.magFilter = source.magFilter
        self.minFilter = source.minFilter

        self.anisotropy = source.anisotropy

        self.format = source.format
        self.type = source.type

        self.offset.copy( source.offset )
        self.repeat.copy( source.repeat )

        self.generateMipmaps = source.generateMipmaps
        self.premultiplyAlpha = source.premultiplyAlpha
        self.flipY = source.flipY
        self.unpackAlignment = source.unpackAlignment
        self.encoding = source.encoding

        return self

    def toJSON(self, meta ):
        if meta.textures[ self.uuid ] is not None:
            return meta.textures[ self.uuid ]

        def getDataURL( image ):
            return image.toData()

        output = {
            'metadata': {
                'version': '4.5',
                'type': 'Texture',
                'generator': 'Texture.toJSON'
            },

            'uuid': self.uuid,
            'name': self.name,

            'mapping': self.mapping,

            'repeat': [ self.repeat.x, self.repeat.y ],
            'offset': [ self.offset.x, self.offset.y ],
            'wrap': [ self.wrapS, self.wrapT ],

            'minFilter': self.minFilter,
            'magFilter': self.magFilter,
            'anisotropy': self.anisotropy,

            'flipY': self.flipY
        }

        if self.image is not None:
            # // TODO: Move to THREE.Image
            image = self.image

            if image.uuid is None:
                image.uuid = _Math.generateUUID()    # // UGH

            if meta.images[ image.uuid ] is None:
                meta.images[ image.uuid ] = {
                    'uuid': image.uuid,
                    'url': getDataURL( image )
                }

            output.image = image.uuid

        meta.textures[ self.uuid ] = output

        return output

    def onDispose(self, callback):
        self.callback = callback

    def dispose(self):
        if self.callback:
            self.callback(self)

    def transformUv(self, uv ):
        if self.mapping != UVMapping:
            return

        uv.multiply( self.repeat )
        uv.add( self.offset )

        if uv.x < 0 or uv.x > 1:
            if self.wrapS == RepeatWrapping:
                uv.x = uv.x - math.floor( uv.x )
            elif self.wrapS == ClampToEdgeWrapping:
                uv.x = 0 if uv.x < 0 else 1
            elif self.wrapS == MirroredRepeatWrapping:
                if abs( math.floor( uv.x ) % 2 ) == 1:
                    uv.x = math.ceil( uv.x ) - uv.x
                else:
                    uv.x = uv.x - math.floor( uv.x )

        if uv.y < 0 or uv.y > 1:
            if self.wrapT == RepeatWrapping:
                uv.y = uv.y - math.floor( uv.y )
            elif self.wrapT == ClampToEdgeWrapping:
                    uv.y = 0 if uv.y < 0 else 1
            elif self.wrapT == MirroredRepeatWrapping:
                    if abs( math.floor( uv.y ) % 2 ) == 1:
                        uv.y = math.ceil( uv.y ) - uv.y
                    else:
                        uv.y = uv.y - math.floor( uv.y )

        if self.flipY:
            uv.y = 1 - uv.y
