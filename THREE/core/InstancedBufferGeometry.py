"""
 * @author benaadams / https://twitter.com/ben_a_adams
"""
from THREE.core.BufferGeometry import *


class InstancedBufferGeometry(BufferGeometry):
    isInstancedBufferGeometry = True
    
    def __init__(self):
        super().__init__( )

        self.set_class(isInstancedBufferGeometry)
        
        self.type = 'InstancedBufferGeometry'
        self.maxInstancedCount = None

    def copy(self, source ):
        super().copy(source)
        self.maxInstancedCount = source.maxInstancedCount
        return self

    def clone(self):
        return type(self)().copy(self)