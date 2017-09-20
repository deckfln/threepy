"""
	/**
	 * @author mrdoob / http://mrdoob.com/
	 * @author alteredq / http://alteredqualia.com/
	 * @author szimek / https://github.com/szimek/
	 */
"""
_textureId = 0

# TODO implement Texture

class Texture:
    def __init__(self, image=None, mapping=None, wrapS=None, wrapT=None, magFilter=None, minFilter=None, format=None, type=None, anisotropy=None, encoding=None ):
        self.image = image