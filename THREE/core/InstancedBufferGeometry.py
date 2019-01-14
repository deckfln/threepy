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

    def copy(self, source, deep=True):
        super().copy(source, deep)
        if hasattr(source, 'maxInstancedCount'):
            self.maxInstancedCount = source.maxInstancedCount
        return self

    def clone(self, deep=True):
        return type(self)().copy(self, deep)
