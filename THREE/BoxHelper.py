"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author Mugen87 / http://github.com/Mugen87
 */
"""
from THREE.objects.LineSegments import *
from THREE.javascriparray import *


class BoxHelper(LineSegments):
    def __init__(self, object=None, color=0xffff00 ):
        self.object = object

        indices = Uint16Array( [ 0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6, 6, 7, 7, 4, 0, 4, 1, 5, 2, 6, 3, 7 ] )
        positions = Float32Array( 8 * 3 )

        geometry = BufferGeometry()
        geometry.setIndex( BufferAttribute( indices, 1 ) )
        geometry.addAttribute( 'position', BufferAttribute( positions, 3 ) )

        super().__init__( geometry, LineBasicMaterial( { 'color': color } ) )

        self.matrixAutoUpdate = False

        self.update()

    def update(self, object=None):
        box = Box3()

        if object is not None:
            print( 'THREE.BoxHelper: .update() has no longer arguments.' )

        if self.object is not None:
            box.setFromObject( self.object )

        if box.isEmpty():
            return

        min = box.min
        max = box.max

        """
        /*
          5____4
        1/___0/|
        | 6__|_7
        2/___3/

        0: max.x, max.y, max.z
        1: min.x, max.y, max.z
        2: min.x, min.y, max.z
        3: max.x, min.y, max.z
        4: max.x, max.y, min.z
        5: min.x, max.y, min.z
        6: min.x, min.y, min.z
        7: max.x, min.y, min.z
        */
        """
        position = self.geometry.attributes.position
        array = position.array

        array[  0 ] = max.x; array[  1 ] = max.y; array[  2 ] = max.z
        array[  3 ] = min.x; array[  4 ] = max.y; array[  5 ] = max.z
        array[  6 ] = min.x; array[  7 ] = min.y; array[  8 ] = max.z
        array[  9 ] = max.x; array[ 10 ] = min.y; array[ 11 ] = max.z
        array[ 12 ] = max.x; array[ 13 ] = max.y; array[ 14 ] = min.z
        array[ 15 ] = min.x; array[ 16 ] = max.y; array[ 17 ] = min.z
        array[ 18 ] = min.x; array[ 19 ] = min.y; array[ 20 ] = min.z
        array[ 21 ] = max.x; array[ 22 ] = min.y; array[ 23 ] = min.z

        position.needsUpdate = True

        self.geometry.computeBoundingSphere()

    def setFromObject(self, object ):
        self.object = object
        self.update()

        return self
