"""
        <title>three.js webgl - cameras</title>
"""
import math
from datetime import datetime

from THREE import *
import THREE._Math as _Math


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
aspect = SCREEN_WIDTH / SCREEN_HEIGHT

camera = None
scene = None
renderer = None
mesh = None
cameraRig = None
activeCamera = None
activeHelper = None
cameraPerspective = None
cameraOrtho = None
cameraPerspectiveHelper = None
cameraOrthoHelper = None
frustumSize = 600


def init():
    global scene, camera, mesh, cameraPerspective, cameraPerspectiveHelper,cameraOrtho,cameraOrthoHelper,activeCamera,activeHelper,frustumSize,cameraRig
    scene = THREE.Scene()

    # //

    camera = THREE.PerspectiveCamera( 50, 0.5 * aspect, 1, 10000 )
    camera.position.z = 2500

    cameraPerspective = THREE.PerspectiveCamera( 50, 0.5 * aspect, 150, 1000 )

    cameraPerspectiveHelper = THREE.CameraHelper( cameraPerspective )
    scene.add( cameraPerspectiveHelper )

    # //
    cameraOrtho = THREE.OrthographicCamera( 0.5 * frustumSize * aspect / - 2, 0.5 * frustumSize * aspect / 2, frustumSize / 2, frustumSize / - 2, 150, 1000 )

    cameraOrthoHelper = THREE.CameraHelper( cameraOrtho )
    scene.add( cameraOrthoHelper )

    # //

    activeCamera = cameraPerspective
    activeHelper = cameraPerspectiveHelper


    # // counteract different front orientation of cameras vs rig

    cameraOrtho.rotation.y = math.pi
    cameraPerspective.rotation.y = math.pi

    cameraRig = THREE.Group()

    cameraRig.add( cameraPerspective )
    cameraRig.add( cameraOrtho )

    scene.add( cameraRig )

    # //

    mesh = THREE.Mesh(
        THREE.SphereBufferGeometry( 100, 16, 8 ),
        THREE.MeshBasicMaterial( { 'color': 0xffffff, 'wireframe': True } )
    )
    scene.add( mesh )

    mesh2 = THREE.Mesh(
        THREE.SphereBufferGeometry( 50, 16, 8 ),
        THREE.MeshBasicMaterial( { 'color': 0x00ff00, 'wireframe': True } )
    )
    mesh2.position.y = 150
    mesh.add( mesh2 )

    mesh3 = THREE.Mesh(
        THREE.SphereBufferGeometry( 5, 16, 8 ),
        THREE.MeshBasicMaterial( { 'color': 0x0000ff, 'wireframe': True } )
    )
    mesh3.position.z = 150
    cameraRig.add( mesh3 )

    # //

    geometry = THREE.Geometry()

    for i in range(10000):
        vertex = THREE.Vector3()
        vertex.x = _Math.randFloatSpread( 2000 )
        vertex.y = _Math.randFloatSpread( 2000 )
        vertex.z = _Math.randFloatSpread( 2000 )

        geometry.vertices.append( vertex )
        if vertex.x == 0 and vertex.y == 0 and vertex.y == 0:
            print( "yoyo")

    particles = THREE.Points( geometry, THREE.PointsMaterial( { 'color': 0x888888 } ) )
    scene.add( particles )

    # //

    # //
    renderer = pyOpenGLRenderer(None, onWindowResize, render, onKeyDown, mouse, motion, animate)
    renderer.setPixelRatio( 1 )
    renderer.setSize( SCREEN_WIDTH, SCREEN_HEIGHT )

    renderer.gammaInput = True
    renderer.gammaOutput = True
    renderer.autoClear = False


    return renderer

# //

def onKeyDown( c, x=0, y=0 ):
    """keyboard callback."""
    global scene, camera, mesh, cameraPerspective, cameraPerspectiveHelper,cameraOrtho,cameraOrthoHelper,activeCamera,activeHelper,frustumSize

    if c == b'q':
        sys.exit(0)

    elif c == b'O':
        activeCamera = cameraOrtho
        activeHelper = cameraOrthoHelper

    elif c == b'P':
        activeCamera = cameraPerspective
        activeHelper = cameraPerspectiveHelper

    glutPostRedisplay()


# //

def onWindowResize( width, height ):
    global scene, camera, mesh, cameraPerspective, cameraPerspectiveHelper,cameraOrtho,cameraOrthoHelper,activeCamera,activeHelper,frustumSize
    global SCREEN_WIDTH, SCREEN_HEIGHT
    """window reshape callback."""

    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize(width, height)

    SCREEN_WIDTH = width
    SCREEN_HEIGHT = height
    aspect = SCREEN_WIDTH / SCREEN_HEIGHT

    camera.aspect = 0.5 * aspect
    camera.updateProjectionMatrix()

    cameraPerspective.aspect = 0.5 * aspect
    cameraPerspective.updateProjectionMatrix()

    cameraOrtho.left   = - 0.5 * frustumSize * aspect / 2
    cameraOrtho.right  =   0.5 * frustumSize * aspect / 2
    cameraOrtho.top    =   frustumSize / 2
    cameraOrtho.bottom = - frustumSize / 2
    cameraOrtho.updateProjectionMatrix()

# //

def animate():
    render()


def render():
    global scene, camera, mesh, cameraPerspective, cameraPerspectiveHelper,cameraOrtho,cameraOrthoHelper,activeCamera,activeHelper,frustumSize,cameraRig

    r = datetime.now().timestamp() * 1

    mesh.position.x = 700 * math.cos( r )
    mesh.position.z = 700 * math.sin( r )
    mesh.position.y = 700 * math.sin( r )

    mesh.children[ 0 ].position.x = 70 * math.cos( 2 * r )
    mesh.children[ 0 ].position.z = 70 * math.sin( r )

    if activeCamera == cameraPerspective:
        cameraPerspective.fov = 35 + 30 * math.sin( 0.5 * r )
        cameraPerspective.far = mesh.position.length()
        cameraPerspective.updateProjectionMatrix()

        cameraPerspectiveHelper.update()
        cameraPerspectiveHelper.visible = True

        cameraOrthoHelper.visible = False
    else:
        cameraOrtho.far = mesh.position.length()
        cameraOrtho.updateProjectionMatrix()

        cameraOrthoHelper.update()
        cameraOrthoHelper.visible = True

        cameraPerspectiveHelper.visible = False

    cameraRig.lookAt( mesh.position )

    renderer.clear()

    activeHelper.visible = False

    renderer.setViewport( 0, 0, SCREEN_WIDTH/2, SCREEN_HEIGHT )
    renderer.render( scene, activeCamera )

    activeHelper.visible = True

    renderer.setViewport( SCREEN_WIDTH/2, 0, SCREEN_WIDTH/2, SCREEN_HEIGHT )
    renderer.render( scene, camera )


def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        rotating = (state == GLUT_DOWN)
    elif button == GLUT_RIGHT_BUTTON:
        scaling = (state == GLUT_DOWN)


def motion(x1, y1):
    glutPostRedisplay()

"""
"""


def main(argv=None):
    global renderer, camera, scene

    renderer = init()
    return renderer.loop()


if __name__ == "__main__":
    sys.exit(main())
