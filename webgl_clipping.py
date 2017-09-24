"""
        <title>three.js webgl - clipping planes</title>
"""
import random
import math
from datetime import datetime
from THREE import *


WIDTH = 640
HEIGHT = 480

camera = None
scene = None
renderer = None
startTime = None
object = None


def init():
    global camera, scene, renderer, startTime, object

    camera = THREE.PerspectiveCamera( 36, WIDTH / HEIGHT, 0.25, 16 )

    camera.position.set( 0, 1.3, 3 )

    scene = THREE.Scene()

    # // Lights

    scene.add( THREE.AmbientLight( 0x505050 ) )

    spotLight = THREE.SpotLight( 0xffffff )
    spotLight.angle = math.pi / 5
    spotLight.penumbra = 0.2
    spotLight.position.set( 2, 3, 3 )
    spotLight.castShadow = True
    spotLight.shadow.camera.near = 3
    spotLight.shadow.camera.far = 10
    spotLight.shadow.mapSize.width = 1024
    spotLight.shadow.mapSize.height = 1024
    scene.add( spotLight )

    dirLight = THREE.DirectionalLight( 0x55505a, 1 )
    dirLight.position.set( 0, 3, 0 )
    dirLight.castShadow = True
    dirLight.shadow.camera.near = 1
    dirLight.shadow.camera.far = 10

    dirLight.shadow.camera.right = 1
    dirLight.shadow.camera.left = - 1
    dirLight.shadow.camera.top    = 1
    dirLight.shadow.camera.bottom = - 1

    dirLight.shadow.mapSize.width = 1024
    dirLight.shadow.mapSize.height = 1024
    scene.add( dirLight )

    # // ***** Clipping planes: *****

    localPlane = THREE.Plane( THREE.Vector3( 0, - 1, 0 ), 0.8 )
    globalPlane = THREE.Plane( THREE.Vector3( - 1, 0, 0 ), 0.1 )

    # // Geometry

    material = THREE.MeshPhongMaterial( {
            'color': 0x80ee10,
            'shininess': 100,
            'side': THREE.DoubleSide,

            # // ***** Clipping setup (material): *****
            'clippingPlanes': [ localPlane ],
            'clipShadows': True

        } )

    geometry = THREE.TorusKnotBufferGeometry( 0.4, 0.08, 95, 20 )

    object = THREE.Mesh( geometry, material )
    object.castShadow = True
    scene.add( object )

    ground = THREE.Mesh(
            THREE.PlaneBufferGeometry( 9, 9, 1, 1 ),
            THREE.MeshPhongMaterial( { 'color': 0xa0adaf, 'shininess': 150 } )
        )

    ground.rotation.x = - math.pi / 2    # // rotates X/Y to X/Z
    ground.receiveShadow = True
    scene.add( ground )


    # // Renderer

    renderer = pyOpenGLRenderer(None, onWindowResize, render, onKeyDown, mouse, motion, animate)
    renderer.setPixelRatio( 1 )
    renderer.setSize( WIDTH, HEIGHT )

    renderer.shadowMap.enabled = True
    renderer.shadowMap.renderSingleSided = False

    # // ***** Clipping setup (renderer): *****
    globalPlanes = [ globalPlane ]
    Empty = []
    renderer.clippingPlanes = Empty     # // GUI sets it to globalPlanes
    renderer.localClippingEnabled = True

    # // Start

    startTime = datetime.now().timestamp()


def onWindowResize(width, height):
    global camera, scene, renderer, startTime, object
    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize( width, height)


def onKeyDown( c, x=0, y=0 ):
    """keyboard callback."""
    global scene, camera, mesh, cameraPerspective, cameraPerspectiveHelper,cameraOrtho,cameraOrthoHelper,activeCamera,activeHelper,frustumSize

    if c == b'q':
        sys.exit(0)

    glutPostRedisplay()


def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        rotating = (state == GLUT_DOWN)
    elif button == GLUT_RIGHT_BUTTON:
        scaling = (state == GLUT_DOWN)


def motion(x1, y1):
    glutPostRedisplay()


def animate():
    global camera, scene, renderer, startTime, object
    currentTime = datetime.now().timestamp()

    time = ( currentTime - startTime ) / 10000

    object.position.y = 0.8
    object.rotation.x += 0.05
    object.rotation.y += 0.02
    object.scale.setScalar( math.cos( time ) * 0.125 + 0.875 )

    render()

def render():
    global camera, scene, renderer, startTime, object
    renderer.render(scene, camera)


def main(argv=None):
    global renderer
    init()
    return renderer.loop()


if __name__ == "__main__":
    sys.exit(main())
