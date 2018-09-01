"""
/**
 * @author WestLangley / http:# //github.com/WestLangley
 * @author zz85 / http:# //github.com/zz85
 * @author bhouston / http:# //clara.io
 *
 * Creates an arrow for visualizing directions
 *
 * Parameters:
 *  dir - Vector3
 *  origin - Vector3
 *  length - Number
 *  color - color in hex value
 *  headLength - Number
 *  headWidth - Number
 */
"""
from THREE.geometries.CylinderGeometry import *
from THREE.objects.Line import *
from THREE.objects.Mesh import *


lineGeometry = None
coneGeometry = None


class  ArrowHelper(Object3D):
    def __init__(self, dir, origin, length=1, color=0xffff00, headLength=None, headWidth=None):
        # // dir is assumed to be normalized
        global lineGeometry, coneGeometry

        super().__init__()

        if headLength is None:
            headLength = 0.2 * length
        if headWidth is None:
                headWidth = 0.2 * headLength

        if lineGeometry is None:
            lineGeometry = BufferGeometry()
            lineGeometry.addAttribute( 'position', Float32BufferAttribute( [ 0, 0, 0, 0, 1, 0 ], 3 ) )

            coneGeometry = CylinderBufferGeometry( 0, 0.5, 1, 5, 1 )
            coneGeometry.translate( 0, - 0.5, 0 )

        self.position.copy( origin )

        self.line = Line( lineGeometry, LineBasicMaterial( { 'color': color } ) )
        self.line.matrixAutoUpdate = False
        self.add( self.line )

        self.cone = Mesh( coneGeometry, MeshBasicMaterial( { 'color': color } ) )
        self.cone.matrixAutoUpdate = False
        self.add( self.cone )

        self.setDirection( dir )
        self.setLength( length, headLength, headWidth )


    def setDirection(self, dir):
        axis = Vector3()

        # // dir is assumed to be normalized

        if dir.y > 0.99999:
            self.quaternion.set( 0, 0, 0, 1 )
        elif dir.y < - 0.99999:
            self.quaternion.set( 1, 0, 0, 0 )

        else:
            axis.set( dir.z, 0, - dir.x ).normalize()

            radians = math.acos( dir.y )

            self.quaternion.setFromAxisAngle( axis, radians )

    def setLength(self, length, headLength=None, headWidth=None ):
        if headLength is None:
            headLength = 0.2 * length
        if headWidth is None:
                headWidth = 0.2 * headLength

        self.line.scale.set( 1, max( 0, length - headLength ), 1 )
        self.line.updateMatrix()

        self.cone.scale.set( headWidth, headLength, headWidth )
        self.cone.position.y = length
        self.cone.updateMatrix()

    def setColor(self, color ):
        self.line.material.color.copy( color )
        self.cone.material.color.copy( color )
