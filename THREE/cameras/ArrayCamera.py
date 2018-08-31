"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.cameras.PerspectiveCamera import *


class ArrayCamera(PerspectiveCamera):
    isArrayCamera = True

    def __init__(self, array=None):
        super().__init__()
        self.set_class(isArrayCamera)

        self.cameras = array or []
