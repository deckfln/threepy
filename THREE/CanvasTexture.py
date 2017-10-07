"""
	/**
	 * @author mrdoob / http://mrdoob.com/
	 */
"""
from THREE.Texture import *


class CanvasTexture(Texture):
    def __init__(self, canvas, mapping=None, wrapS=None, wrapT=None, magFilter=None, minFilter=None, format=None, type=None, anisotropy=None ):
        super().__init__( canvas, mapping, wrapS, wrapT, magFilter, minFilter, format, type, anisotropy )

        self.needsUpdate = True