"""
        <title>three.js webgl - clipIntersection</title>
"""
import sys
import random

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.TrackballControls import *
from THREE.Constants import *
from THREE.controls.OrbitControls import *
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.clipIntersection = True
        self.planeConstant = True
        self.showHelpers = True
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None


def init(p):
    clipPlanes = [
        THREE.Plane(THREE.Vector3(1, 0, 0), 0),
        THREE.Plane(THREE.Vector3(0, - 1, 0), 0),
        THREE.Plane(THREE.Vector3(0, 0, - 1), 0)
    ]

    p.container = pyOpenGL(p)
    p.renderer = THREE.pyOpenGLRenderer( { 'antialias': True } )
    p.renderer.localClippingEnabled = True

    p.scene = THREE.Scene()

    p.camera = THREE.PerspectiveCamera( 40, window.innerWidth / window.innerHeight, 1, 200 )

    p.camera.position.set( - 20, 30, 40 )

    p.controls = OrbitControls( p.camera, p.container )
    p.controls.minDistance = 10
    p.controls.maxDistance = 100
    p.controls.enablePan = False

    light = THREE.HemisphereLight( 0xffffff, 0x080808, 1 )
    p.scene.add( light )

    p.scene.add( THREE.AmbientLight( 0x505050 ) )

    # //

    group = THREE.Group()

    for i in range(1, 25):
        geometry = THREE.SphereBufferGeometry( i / 2, 48, 24 )

        material = THREE.MeshLambertMaterial( {
            'color': THREE.Color( math.sin( i * 0.5 ) * 0.5 + 0.5, math.cos( i * 1.5 ) * 0.5 + 0.5, math.sin( i * 4.5 + 0 ) * 0.5 + 0.5 ),
            'side': THREE.DoubleSide,
            'clippingPlanes': clipPlanes,
            'clipIntersection': p.clipIntersection
        } )

        group.add( THREE.Mesh( geometry, material ) )

    p.scene.add( group )

    # // helpers

    helpers = THREE.Group()
    helpers.add( THREE.AxisHelper( 20 ) )
    helpers.add( THREE.PlaneHelper( clipPlanes[ 0 ], 30, 0xff0000 ) )
    helpers.add( THREE.PlaneHelper( clipPlanes[ 1 ], 30, 0x00ff00 ) )
    helpers.add( THREE.PlaneHelper( clipPlanes[ 2 ], 30, 0x0000ff ) )
    helpers.visible = True
    p.scene.add( helpers )

    p.container.addEventListener( 'resize', onWindowResize, False )
    p.container.addEventListener( 'animationRequest', render, False )


def onWindowResize(event, p):
    height = event.height
    width = event.width

    p.camera.aspect = width / height
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( width, height )


def animate(p):
    render(p)


def render(p):
    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
