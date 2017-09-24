"""
        <title>three.js webgl - arraycamera</title>
"""
import math
from datetime import datetime

from THREE import *
import THREE._Math as _Math

camera = None
scene = None
renderer = None
mesh = None

WIDTH, HEIGHT = 640,480


def init():
    global scene, camera, mesh, renderer

    AMOUNT = 6
    SIZE = 1 / AMOUNT
    ASPECT_RATIO = WIDTH / HEIGHT

    cameras = []

    for y in range(AMOUNT):
        for x in range(AMOUNT):
            subcamera = THREE.PerspectiveCamera( 40, ASPECT_RATIO, 0.1, 10 )
            subcamera.bounds = THREE.Vector4( x / AMOUNT, y / AMOUNT, SIZE, SIZE )
            subcamera.position.x = ( x / AMOUNT ) - 0.5
            subcamera.position.y = 0.5 - ( y / AMOUNT )
            subcamera.position.z = 1.5
            subcamera.position.multiplyScalar( 2 )
            subcamera.lookAt( THREE.Vector3() )
            subcamera.updateMatrixWorld()
            cameras.append( subcamera )

    camera = THREE.ArrayCamera( cameras )
    camera.position.z = 3

    scene = THREE.Scene()

    scene.add( THREE.AmbientLight( 0x222244 ) )

    light = THREE.DirectionalLight()
    light.position.set( 0.5, 0.5, 1 )
    light.castShadow = True
    light.shadow.camera.zoom = 4    # // tighter shadow map
    scene.add( light )

    geometry = THREE.PlaneBufferGeometry( 100, 100 )
    material = THREE.MeshPhongMaterial( { 'color': 0x000066 } )

    background = THREE.Mesh( geometry, material )
    background.receiveShadow = True
    background.position.set( 0, 0, - 1 )
    scene.add( background )

    geometry = THREE.CylinderBufferGeometry( 0.5, 0.5, 1, 32 )
    material = THREE.MeshPhongMaterial( { 'color': 0xff0000 } )

    mesh = THREE.Mesh( geometry, material )
    mesh.castShadow = True
    mesh.receiveShadow = True
    scene.add( mesh )

    # //
    renderer = pyOpenGLRenderer(None, onWindowResize, render, onKeyDown, mouse, motion, animate)
    renderer.setPixelRatio( 1 )
    renderer.setSize( WIDTH, HEIGHT )

    renderer.gammaInput = True
    renderer.gammaOutput = True

    renderer.shadowMap.enabled = True


def animate():
    global scene, camera, mesh, renderer

    mesh.rotation.x += 0.01
    mesh.rotation.z += 0.02

    render()


def render():
    global renderer
    renderer.render( scene, camera )


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
    renderer.setSize(width, height)

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
    global renderer

    init()
    return renderer.loop()


if __name__ == "__main__":
    sys.exit(main())
