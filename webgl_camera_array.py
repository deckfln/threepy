"""
        <title>three.js webgl - arraycamera</title>
"""
import math
from datetime import datetime

from THREE import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.mesh = None


def init(p):
    p.container = pyOpenGL(p)

    AMOUNT = 6
    SIZE = 1 / AMOUNT
    ASPECT_RATIO = window.innerWidth / window.innerHeight

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

    p.camera = THREE.ArrayCamera( cameras )
    p.camera.position.z = 3

    p.scene = THREE.Scene()

    p.scene.add( THREE.AmbientLight( 0x222244 ) )

    light = THREE.DirectionalLight()
    light.position.set( 0.5, 0.5, 1 )
    light.castShadow = True
    light.shadow.camera.zoom = 4    # // tighter shadow map
    p.scene.add( light )

    geometry = THREE.PlaneBufferGeometry( 100, 100 )
    material = THREE.MeshPhongMaterial( { 'color': 0x000066 } )

    background = THREE.Mesh( geometry, material )
    background.receiveShadow = True
    background.position.set( 0, 0, - 1 )
    p.scene.add( background )

    geometry = THREE.CylinderBufferGeometry( 0.5, 0.5, 1, 32 )
    material = THREE.MeshPhongMaterial( { 'color': 0xff0000 } )

    p.mesh = THREE.Mesh( geometry, material )
    p.mesh.castShadow = True
    p.mesh.receiveShadow = True
    p.scene.add( p.mesh )

    # //
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize( window.innerWidth, window.innerHeight )
    p.container.addEventListener( 'resize', onWindowResize, False )

    p.renderer.shadowMap.enabled = True


def animate(p):
    p.mesh.rotation.x += 0.01
    p.mesh.rotation.z += 0.02

    render(p)


def render(p):
    p.renderer.render( p.scene, p.camera )


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


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize(window.innerWidth, window.innerHeight)


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
