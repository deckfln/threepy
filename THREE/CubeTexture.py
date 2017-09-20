"""
/ **
  * @ author mrdoob / http: // mrdoob.com /
  * /
"""

from THREE.Texture import *

# TODO implement cubetexture
class CubeTexture(Texture):
    def __init__(self, images=None, mapping=None, wrapS=None, wrapT=None, magFilter=None, minFilter=None, format=None, type=None, anisotropy=None, encoding=None):
        self.image = images
