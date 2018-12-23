"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author alteredq / http:# //alteredqualia.com/
 * @author szimek / https:# //github.com/szimek/
 */
"""
import numpy as np

import THREE._Math as _Math
from THREE.math.Vector2 import *
from THREE.math.Matrix3 import *
import THREE.Global

_textureId = 0


class Texture(pyOpenGLObject):
    DEFAULT_IMAGE = None
    DEFAULT_MAPPING = UVMapping
    isTexture = True
    
    def __init__(self, image=None, mapping=None, wrapS=None, wrapT=None, magFilter=None, minFilter=None, format=None, gltype=None, anisotropy=None, encoding=None):
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
        self.mipmaps = None

        self.mapping = mapping if mapping is not None else Texture.DEFAULT_MAPPING

        self.wrapS = wrapS if wrapS is not None else ClampToEdgeWrapping
        self.wrapT = wrapT if wrapT is not None else ClampToEdgeWrapping

        self.magFilter = magFilter if magFilter is not None else LinearFilter
        self.minFilter = minFilter if minFilter is not None else LinearMipMapLinearFilter

        self.anisotropy = anisotropy if anisotropy is not None else 1

        if image is not None:
            if type(image) is list:
                if image[0] is not None:
                    self.format = RGBFormat if image[0].mode == 'RGB' else RGBAFormat
                else:
                    self.format = format if format is not None else RGBAFormat
            else:
                self.format = RGBFormat if image.mode == 'RGB' else RGBAFormat
        else:
            self.format = format if format is not None else RGBAFormat

        self.type = gltype if gltype is not None else UnsignedByteType

        self.offset = Vector2(0, 0)
        self.repeat = Vector2(1, 1)
        self.center = Vector2(0, 0)
        self.rotation = 0

        self.matrixAutoUpdate = True
        self.matrix = Matrix3()

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

    def get_data(self):
        if self.img_data is None:
            self.img_data = np.fromstring(self.image.tobytes(), np.uint8)

        return self.img_data

    def set(self, value ):
        if value:
            self.version += 1

    needsUpdate = property(None, set)

    def updateMatrix(self):
        self.matrix.setUvTransform(self.offset.x, self.offset.y, self.repeat.x, self.repeat.y, self.rotation,
                                   self.center.x, self.center.y)

    def clone(self):
        return type(self)().copy( self )

    def copy(self, source ):
        self.name = source.name

        self.image = source.image
        self.mipmaps = source.mipmaps[:] if source.mipmaps is not None else None

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
        self.center.copy(source.center)
        self.rotation = source.rotation

        self.matrixAutoUpdate = source.matrixAutoUpdate
        self.matrix.copy(source.matrix)

        self.generateMipmaps = source.generateMipmaps
        self.premultiplyAlpha = source.premultiplyAlpha
        self.flipY = source.flipY
        self.unpackAlignment = source.unpackAlignment
        self.encoding = source.encoding

        return self

    def toJSON(self, meta ):
        isRootObject = meta is None or type(meta) is str

        if not isRootObject and meta.textures[self.uuid] is not None:
            return meta.textures[self.uuid]

        if meta.textures[ self.uuid ] is not None:
            return meta.textures[ self.uuid ]

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
            'center': [self.center.x, self.center.y],
            'rotation': self.rotation,

            'wrap': [ self.wrapS, self.wrapT ],

            'format': self.format,
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

            if not isRootObject and meta.images[image.uuid] is None:
                if type(image) is list:
                    # process array of images e.g.CubeTexture
                    url = []

                    for i in range(len(image)):
                        url.append( ImageUtils.getDataURL( image[i] ) )
                else:
                    # process single image
                    url = ImageUtils.getDataURL( image )

                meta.images[ image.uuid ] = {
                    'uuid': image.uuid,
                    'url': url
                }

            if not isRootObject:
                output.image = image.uuid

        meta.textures[ self.uuid ] = output

        return output

    def dispose(self):
        THREE.Global.dispose_properties_queue.append(self)

    def transformUv(self, uv ):
        if self.mapping != UVMapping:
            return

        uv.applyMatrix3(self.matrix)

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
