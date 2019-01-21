"""
        <title>three.js webgl - clipping planes</title>
"""
import random
import math
import sys
from datetime import datetime
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.startTime = None
        self.object = None


def init(p):
    p.container = pyOpenGL(p)

    p.camera = THREE.PerspectiveCamera( 36, window.innerWidth / window.innerHeight, 0.25, 16 )

    p.camera.position.set( 0, 1.3, 3 )

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
    p.scene.add( dirLight )

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

    p.object = THREE.Mesh( geometry, material )
    p.object.castShadow = True
    p.scene.add( p.object )

    ground = THREE.Mesh(
            THREE.PlaneBufferGeometry( 9, 9, 1, 1 ),
            THREE.MeshPhongMaterial( { 'color': 0xa0adaf, 'shininess': 150 } )
        )

    ground.rotation.x = - math.pi / 2    # // rotates X/Y to X/Z
    ground.receiveShadow = True
    p.scene.add( ground )


    # // Renderer

    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize( window.innerWidth, window.innerHeight )
    p.container.addEventListener( 'resize', onWindowResize, False )

    p.renderer.shadowMap.enabled = True

    # // ***** Clipping setup (renderer): *****
    globalPlanes = [ globalPlane ]
    Empty = []
    p.renderer.clippingPlanes = Empty     # // GUI sets it to globalPlanes
    p.renderer.localClippingEnabled = True

    # // Start

    p.startTime = datetime.now().timestamp()


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( window.innerWidth, window.innerHeight )


def onKeyDown( event, p ):
    """keyboard callback."""
    if evenr["keycode"] == 113: # q
        sys.exit(0)


def animate(p):
    currentTime = datetime.now().timestamp()

    time = ( currentTime - p.startTime ) / 10000

    p.object.position.y = 0.8
    p.object.rotation.x += 0.05
    p.object.rotation.y += 0.02
    p.object.scale.setScalar( math.cos( time ) * 0.125 + 0.875 )

    render(p)


def render(p):
    p.renderer.render(p.scene, p.camera)


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
