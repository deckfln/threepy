"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author bhouston / http:# //clara.io/
 * @author stephomi / http:# //stephaneginier.com/
 */
"""
from THREE.Ray import *


def ascSort( a):
    return a.distance


def intersectObject( object, raycaster, intersects, recursive=False ):
    if object.visible == False:
        return

    object.raycast( raycaster, intersects )

    if recursive == True:
        children = object.children

        for i in range(len(children)):
            intersectObject( children[ i ], raycaster, intersects, True )


class Raycaster:
    linePrecision = 1
    
    def __init__(self, origin=None, direction=None, near=0, far=float("+inf") ):
        self.ray = Ray( origin, direction )

        # // direction is assumed to be normalized (for accurate distance calculations)

        self.near = near
        self.far = far

        self.params = {
            'Mesh': {},
            'Line': {},
            'LOD': {},
            'Points': { 'threshold': 1 },
            'Sprite': {}
        }

    def getPointCloud(self):
        print( 'THREE.Raycaster: params.PointCloud has been renamed to params.Points.' )
        return self.params['Points']

    PointCloud = property(getPointCloud)

    def set(self, origin, direction ):
        # // direction is assumed to be normalized (for accurate distance calculations)
        self.ray.set( origin, direction )

    def setFromCamera(self, coords, camera ):
        if camera and camera.isPerspectiveCamera:
            self.ray.origin.setFromMatrixPosition( camera.matrixWorld )
            self.ray.direction.set( coords.x, coords.y, 0.5 ).unproject( camera ).sub( self.ray.origin ).normalize()

        elif camera and camera.isOrthographicCamera:
            self.ray.origin.set( coords.x, coords.y, ( camera.near + camera.far ) / ( camera.near - camera.far ) ).unproject( camera )  # // set origin in plane of camera
            self.ray.direction.set( 0, 0, - 1 ).transformDirection( camera.matrixWorld )

        else:
            raise RuntimeError( 'THREE.Raycaster: Unsupported camera type.' )


    def intersectObject(self, object, recursive ):
        intersects = []

        intersectObject( object, self, intersects, recursive )

        intersects.sort( ascSort )

        return intersects

    def intersectObjects(self, objects, recursive=False ):
        intersects = []

        if isinstance(objects, list) == False:
            print( 'THREE.Raycaster.intersectObjects: objects is not an Array.' )
            return intersects

        for i in range(len(objects)):
            intersectObject( objects[ i ], self, intersects, recursive )

        intersects.sort( key=ascSort )

        return intersects
