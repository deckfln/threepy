"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.javascriparray import *


def absNumericalSort( a):
    return -abs(a[ 1 ])

    
class pyOpenGLMorphtargets:
    def __init__( self ):
        self.influencesList = {}
        self.morphInfluences = Float32Array( 8 )

    def update(self, object, geometry, material, program ):
        objectInfluences = object.morphTargetInfluences

        length = len(objectInfluences)

        if geometry.id not in self.influencesList:
            # initialise list
            influences = [[i, 0] for i in range(length)]
            self.influencesList[ geometry.id ] = influences
        else:
            influences = self.influencesList[geometry.id]

        morphTargets = material.morphTargets and geometry.morphAttributes.position
        morphNormals = material.morphNormals and geometry.morphAttributes.normal

        # Remove current morphAttributes

        debug = ""
        i = 0
        for influence in influences:
            if influence[ 1 ] != 0:
                if morphTargets:
                    geometry.removeAttribute( 'morphTarget%d' % i )
                    debug += 'remove morphTarget%d ' % i
                if morphNormals:
                    geometry.removeAttribute( 'morphNormal%d' % i )
            i += 1

        # Collect influences

        i = 0
        for influence in influences:
            influence[ 0 ] = i
            influence[ 1 ] = objectInfluences[ i ]
            i += 1

        influences.sort( key = absNumericalSort )

        # Add morphAttributes

        for i in range(8):
            influence = influences[i]
            if influence:
                index = influence[ 0 ]
                value = influence[ 1 ]

                if value:
                    if morphTargets:
                        geometry.addAttribute( 'morphTarget%d' % i, morphTargets[ index ] )
                    if morphNormals:
                        geometry.addAttribute( 'morphNormal%d' % i, morphNormals[ index ] )

                    self.morphInfluences[ i ] = value
                    continue

            self.morphInfluences[ i ] = 0

        program.getUniforms().setValue( 'morphTargetInfluences', self.morphInfluences )
