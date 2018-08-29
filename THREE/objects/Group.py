"""
    /**
     * @author mrdoob / http://mrdoob.com/
     */
"""
from THREE.core.Object3D import *


class Group(Object3D):
    isGroup: True

    def __init__(self):
        super().__init__()
        self.type = 'Group'
        self.skeleton = None
        self.set_class(isGroup)
