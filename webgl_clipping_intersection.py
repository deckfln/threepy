"""
        <title>three.js webgl - clipIntersection</title>
"""
import sys
import random

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.TrackballControls import *
from THREE.Constants import *

camera = None
scene = None
renderer = None
container = None


class Params:
    def __init__(self):
        self.clipIntersection = True
        self.planeConstant = True
        self.showHelpers = True


params = Params()

clipPlanes = [
    THREE.Plane( THREE.Vector3( 1, 0, 0 ), 0 ),
    THREE.Plane( THREE.Vector3( 0, - 1, 0 ), 0 ),
    THREE.Plane( THREE.Vector3( 0, 0, - 1 ), 0 )
]


def init():
    global camera, scene, renderer, container
    
    container = pyOpenGL()
    renderer = THREE.pyOpenGLRenderer( { 'antialias': True } )
    size = renderer.getSize()
    renderer.localClippingEnabled = True

    scene = THREE.Scene()

    camera = THREE.PerspectiveCamera( 40, size['width'] / size['height'], 1, 200 )

    camera.position.set( - 20, 30, 40 )

    controls = THREE.OrbitControls( camera, container )
    controls.minDistance = 10
    controls.maxDistance = 100
    controls.enablePan = False

    light = THREE.HemisphereLight( 0xffffff, 0x080808, 1 )
    scene.add( light )

    scene.add( THREE.AmbientLight( 0x505050 ) )

    # //

    group = THREE.Group()

    for i in range(1, 25):
        geometry = THREE.SphereBufferGeometry( i / 2, 48, 24 )

        material = THREE.MeshLambertMaterial( {
            'color': THREE.Color( math.sin( i * 0.5 ) * 0.5 + 0.5, math.cos( i * 1.5 ) * 0.5 + 0.5, math.sin( i * 4.5 + 0 ) * 0.5 + 0.5 ),
            'side': THREE.DoubleSide,
            'clippingPlanes': clipPlanes,
            'clipIntersection': params.clipIntersection
        } )

        group.add( THREE.Mesh( geometry, material ) )

    scene.add( group )

    # // helpers

    helpers = THREE.Group()
    helpers.add( THREE.AxisHelper( 20 ) )
    helpers.add( THREE.PlaneHelper( clipPlanes[ 0 ], 30, 0xff0000 ) )
    helpers.add( THREE.PlaneHelper( clipPlanes[ 1 ], 30, 0x00ff00 ) )
    helpers.add( THREE.PlaneHelper( clipPlanes[ 2 ], 30, 0x0000ff ) )
    helpers.visible = True
    scene.add( helpers )

    container.addEventListener( 'resize', onWindowResize, False )
    container.addEventListener( 'animationRequest', render, False )


def onWindowResize(event):
    global camera, controls, scene, renderer, cross, container
    height = event.height
    width = event.width

    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize( width, height )


def render():
    global camera, scene, renderer, container
    
    renderer.render( scene, camera )


def main(argv=None):
    global container
    init()
    return container.loop()


if __name__ == "__main__":
    sys.exit(main())
