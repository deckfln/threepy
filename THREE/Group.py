"""
    /**
     * @author mrdoob / http://mrdoob.com/
     */
"""
from THREE.Object3D import *


class Group(Object3D):
    def __init__(self):
        super().__init__()
        self.type = 'Group'
