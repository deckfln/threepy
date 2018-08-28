"""
/**
 * @author WestLangley / http://github.com/WestLangley
 */
"""
from THREE.Line import *
from THREE.Mesh import *


class PlaneHelper(Line):
    def __init__(self, plane, size=1, hex=0xffff00 ):
        super().__init__()
        self.type = 'PlaneHelper'

        self.plane = plane

        self.size = size 

        color = hex

        positions = [ 1, - 1, 1, - 1, 1, 1, - 1, - 1, 1, 1, 1, 1, - 1, 1, 1, - 1, - 1, 1, 1, - 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0 ]

        geometry = BufferGeometry()
        geometry.addAttribute( 'position', Float32BufferAttribute( positions, 3 ) )
        geometry.computeBoundingSphere()

        super().__init__(geometry, LineBasicMaterial( { 'color': color } ) )

        # //

        positions2 = [ 1, 1, 1, - 1, 1, 1, - 1, - 1, 1, 1, 1, 1, - 1, - 1, 1, 1, - 1, 1 ]

        geometry2 = BufferGeometry()
        geometry2.addAttribute( 'position', Float32BufferAttribute( positions2, 3 ) )
        geometry2.computeBoundingSphere()

        self.add( Mesh( geometry2, MeshBasicMaterial( { 'color': color, 'opacity': 0.2, 'transparent': True, 'depthWrite': False } ) ) )

        # //

        self.onBeforeRender()

    def onBeforeRender(self, renderer=None, scene=None, camera=None, geometry=None, material=None, group=None):
        scale = - self.plane.constant

        if abs( scale ) < 1e-8:
            scale = 1e-8    # // sign does not matter

        self.scale.set( 0.5 * self.size, 0.5 * self.size, scale )

        self.lookAt( self.plane.normal )

        self.updateMatrixWorld()
