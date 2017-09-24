"""
	/**
	 * @author mrdoob / http://mrdoob.com/
	 */
"""
from THREE.Camera import *


class ArrayCamera(PerspectiveCamera):
    isArrayCamera = True

    def __init__(self, array=None ):
        super().__init__()
        self.cameras = array or []