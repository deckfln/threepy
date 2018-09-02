"""
    /**
     * @author alteredq / http://alteredqualia.com/
     */
"""
from THREE.core.Object3D import *


class ImmediateRenderObject(Object3D):
    isImmediateRenderObject = True

    def __init__(self, material):
        super().__init__()
        self.set_class(isImmediateRenderObject)

        self.material = material
        self.render = None

