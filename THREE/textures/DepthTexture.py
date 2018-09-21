"""
 * @author Matt DesLauriers / @mattdesl
 * @author atix / arthursilber.de
"""

from THREE.textures.Texture import  *
from THREE.Constants import *


class _depthImage:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class DepthTexture(Texture):
    isDepthTexture = True

    def __init__(self, width=32, height=32, type=None, mapping=None, wrapS=ClampToEdgeWrapping, wrapT=ClampToEdgeWrapping, magFilter=NearestFilter, minFilter=NearestFilter, anisotropy=1, format=DepthFormat ):
        if format != DepthFormat and format != DepthStencilFormat:
            raise RuntimeWarning( 'DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat' )

        if type is None:
            if format == DepthFormat:
                type = UnsignedShortType
            if format == DepthStencilFormat:
                type = UnsignedInt248Type

        super().__init__(None, mapping, wrapS, wrapT, magFilter, minFilter, format, type, anisotropy )
        self.set_class(isDepthTexture)

        self.image = _depthImage(width, height)

        self.flipY = False
        self.generateMipmaps = False
