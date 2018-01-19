"""
 * @author benaadams / https://twitter.com/ben_a_adams
"""
from THREE.BufferGeometry import *


class InstancedBufferGeometry(BufferGeometry):
    isInstancedBufferGeometry = True
    
    def __init__(self):
        super().__init__( )

        self.set_class(isInstancedBufferGeometry)
        
        self.type = 'InstancedBufferGeometry'
        self.maxInstancedCount = None

    def addGroup(self, start, count, materialIndex ):
        self.groups.push( {
            'start': start,
            'count': count,
            'materialIndex': materialIndex
        } )

    def copy(self, source ):
        index = source.index

        if index is not None:
            self.setIndex( index.clone() )

        attributes = source.attributes
        
        for name in attributes:
            attribute = attributes[ name ]
            self.addAttribute( name, attribute.clone() )

        groups = source.groups
        
        for group in groups:
            self.addGroup( group.start, group.count, group.materialIndex )

        return self
