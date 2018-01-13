"""
        <title>three.js webgl - clipping planes</title>
"""
import random
import math
import sys
from datetime import datetime
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.pyOpenGL.pyOpenGL import *


def planesFromMesh( vertices, indices ):
    """
    # // creates a clipping volume from a convex triangular mesh
    # // specified by the arrays 'vertices' and 'indices'
    """
    n = int(len(indices) / 3)
    result = [ None for i in range(n)]

    j = 0
    for i in range(n):
        a = vertices[ indices[   j   ] ]
        b = vertices[ indices[ j + 1 ] ]
        c = vertices[ indices[ j + 2 ] ]

        result[ i ] = THREE.Plane().setFromCoplanarPoints( a, b, c )
        j += 3

    return result


def createPlanes( n ):
    """
    # // creates an array of n uninitialized plane objects
    """
    result = [None for i in range(n)]

    for i in range(n):
        result[ i ] = THREE.Plane()

    return result

    
def assignTransformedPlanes( planesOut, planesIn, matrix ):
    """
    # // sets an array of existing planes to transformed 'planesIn'
    """
    for i in range(len(planesIn)):
        planesOut[ i ].copy( planesIn[ i ] ).applyMatrix4( matrix )


def cylindricalPlanes( n, innerRadius ):
    """
    """
    result = createPlanes( n )

    for i in range(n):
        plane = result[ i ]
        angle = i * math.pi * 2 / n

        plane.normal.set(math.cos( angle ), 0, math.sin( angle ) )

        plane.constant = innerRadius

    return result


def planeToMatrix(plane):
    """
    # // creates a matrix that aligns X/Y to a given plane
    """
    # // temporaries:
    xAxis = THREE.Vector3()
    yAxis = THREE.Vector3()
    trans = THREE.Vector3()

    zAxis = plane.normal
    matrix = THREE.Matrix4()

    # // Hughes & Moeller '99
    # // "Building an Orthonormal Basis from a Unit Vector."

    if abs( zAxis.x ) > abs( zAxis.z ):
        yAxis.set( -zAxis.y, zAxis.x, 0 )
    else:
        yAxis.set( 0, -zAxis.z, zAxis.y )

    xAxis.crossVectors( yAxis.normalize(), zAxis )

    plane.coplanarPoint( trans )
    return matrix.set(
        xAxis.x, yAxis.x, zAxis.x, trans.x,
        xAxis.y, yAxis.y, zAxis.y, trans.y,
        xAxis.z, yAxis.z, zAxis.z, trans.z,
            0,        0,        0,            1 )

# // A regular tetrahedron for the clipping volume:

SQRT1_2 = math.sqrt(1/2)
Vertices = [
        THREE.Vector3( + 1,   0, + SQRT1_2 ),
        THREE.Vector3( - 1,   0, + SQRT1_2 ),
        THREE.Vector3(   0, + 1, - SQRT1_2 ),
        THREE.Vector3(   0, - 1, - SQRT1_2 )
    ]

Indices = [
    0, 1, 2,    0, 2, 3,    0, 3, 1,    1, 3, 2
]

Planes = planesFromMesh( Vertices, Indices )
PlaneMatrices = [ planeToMatrix(plane) for plane in Planes ]

GlobalClippingPlanes = cylindricalPlanes( 5, 3.5 )

Empty = []

class Params:
    def __init__(self):
        self.container = None
        self.camera = None
        self.scene = None
        self.renderer = None
        self.startTime = None

        self.object = None
        self.clipMaterial = None
        self.volumeVisualization = None
        self.globalClippingPlanes = None
        self.clipMaterial = None


def init(p):
    p.container = pyOpenGL(p)
    p.camera = THREE.PerspectiveCamera(36, window.innerWidth / window.innerHeight, 0.25, 16 )

    p.camera.position.set( 0, 1.5, 3 )

    p.scene = THREE.Scene()

    # // Lights

    p.scene.add( THREE.AmbientLight( 0x505050 ) )

    spotLight = THREE.SpotLight( 0xffffff )
    spotLight.angle = math.pi / 5
    spotLight.penumbra = 0.2
    spotLight.position.set( 2, 3, 3 )
    spotLight.castShadow = True
    spotLight.shadow.camera.near = 3
    spotLight.shadow.camera.far = 10
    spotLight.shadow.mapSize.width = 1024
    spotLight.shadow.mapSize.height = 1024
    p.scene.add( spotLight )

    dirLight = THREE.DirectionalLight( 0x55505a, 1 )
    dirLight.position.set( 0, 2, 0 )
    dirLight.castShadow = True
    dirLight.shadow.camera.near = 1
    dirLight.shadow.camera.far = 10

    dirLight.shadow.camera.right = 1
    dirLight.shadow.camera.left = - 1
    dirLight.shadow.camera.top    = 1
    dirLight.shadow.camera.bottom = - 1

    dirLight.shadow.mapSize.width = 1024
    dirLight.shadow.mapSize.height = 1024
    p.scene.add( dirLight )

    # // Geometry

    p.clipMaterial = THREE.MeshPhongMaterial( {
        'color': 0xee0a10,
        'shininess': 100,
        'side': THREE.DoubleSide,
        # // Clipping setup:
        'clippingPlanes': createPlanes( len(Planes) ),
        'clipShadows': True
    } )

    p.object = THREE.Group()

    geometry = THREE.BoxBufferGeometry( 0.18, 0.18, 0.18 )

    for z in range(-2, 3):
        for y in range(-2, 3):
            for x in range(-2, 3):
                mesh = THREE.Mesh( geometry, p.clipMaterial )
                mesh.position.set( x / 5, y / 5, z / 5 )
                mesh.castShadow = True
                p.object.add( mesh )

    p.scene.add( p.object )

    planeGeometry =THREE.PlaneBufferGeometry( 3, 3, 1, 1 )
    color = THREE.Color()

    p.volumeVisualization = THREE.Group()
    p.volumeVisualization.visible = False

    for i in range(len(Planes)):
        m = p.clipMaterial.clippingPlanes[:]
        del m[i]

        material = THREE.MeshBasicMaterial( {
            'color':  color.setHSL( i / len(Planes), 0.5, 0.5 ).getHex(),
            'side': THREE.DoubleSide,

            'opacity': 0.2,
            'transparent': True,

            # // clip to the others to show the volume (wildly
            # // intersecting transparent planes look bad)
            'clippingPlanes': m,

            # // no need to enable shadow clipping - the plane
            # // visualization does not cast shadows
        } )

        p.volumeVisualization.add(
                THREE.Mesh( planeGeometry, material ) )

    p.scene.add( p.volumeVisualization )

    ground = THREE.Mesh( planeGeometry,
            THREE.MeshPhongMaterial( {
                'color': 0xa0adaf, 'shininess': 150 } ) )
    ground.rotation.x = - math.pi / 2
    ground.scale.multiplyScalar( 3 )
    ground.receiveShadow = True
    p.scene.add( ground )

    # // Renderer

    p.renderer = THREE.pyOpenGLRenderer()
    p.renderer.shadowMap.enabled = True
    p.renderer.shadowMap.renderSingleSided = False
    p.container.addEventListener( 'resize', onWindowResize)

    # // Clipping setup:
    p.globalClippingPlanes = createPlanes(len(GlobalClippingPlanes))
    p.renderer.clippingPlanes = Empty
    p.renderer.localClippingEnabled = True

    # // Start

    p.startTime = datetime.now().timestamp()


def onWindowResize(event, p):
    p.camera.aspect = event.width / event.height
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( event.width, event.height )


def setObjectWorldMatrix(p, object, matrix ):
    # // set the orientation of an object based on a world matrix

    parent = object.parent
    p.scene.updateMatrixWorld()
    object.matrix.getInverse( parent.matrixWorld )
    object.applyMatrix( matrix )


transform = THREE.Matrix4()
tmpMatrix = THREE.Matrix4()


def animate(p):
    global transform, tmpMatrix

    currentTime = datetime.now().timestamp()
    time = ( currentTime - p.startTime ) / 10

    if time > 2:
        sys.exit()

    p.object.position.y = 1
    p.object.rotation.x = time * 0.5
    p.object.rotation.y = time * 0.2

    p.object.updateMatrix()
    transform.copy( p.object.matrix )

    bouncy = math.cos( time * .5 ) * 0.5 + 0.7
    transform.multiply(tmpMatrix.makeScale( bouncy, bouncy, bouncy ) )

    assignTransformedPlanes(p.clipMaterial.clippingPlanes, Planes, transform )

    planeMeshes = p.volumeVisualization.children

    for i in range(len(planeMeshes)):
        tmpMatrix.multiplyMatrices( transform, PlaneMatrices[ i ] )
        setObjectWorldMatrix(p, planeMeshes[ i ], tmpMatrix )

    transform.makeRotationY( time * 0.1 )

    assignTransformedPlanes(p.globalClippingPlanes, GlobalClippingPlanes, transform )

    p.renderer.render( p.scene, p.camera )


def onKeyDown( c, x=0, y=0 ):
    if c == 113: # q
        sys.exit(0)


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
