"""
        <title>three.js webgl - trackball controls</title>
"""
import sys
import random

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.TrackballControls import *
from THREE.Constants import *


container = None
camera = None
controls = None
scene = None
renderer = None

cross = None


def init():
    global camera, controls, scene, renderer, cross, container

    container = pyOpenGL()
    container.addEventListener( 'resize', onWindowResize, False )
    container.addEventListener( 'animationRequest', animate )

    renderer = pyOpenGLRenderer({ 'antialias': False })
    size = renderer.getSize()

    camera = THREE.PerspectiveCamera( 60, size['width'] / size['height'], 1, 1000 )
    camera.position.z = 500

    controls = THREE.TrackballControls( camera, container )

    controls.rotateSpeed = 1.0
    controls.zoomSpeed = 1.2
    controls.panSpeed = 0.8

    controls.noZoom = False
    controls.noPan = False

    controls.staticMoving = True
    controls.dynamicDampingFactor = 0.3

    controls.keys = [ 65, 83, 68 ]

    # controls.addEventListener( 'change', render )

    # // world

    scene = THREE.Scene()
    scene.background = THREE.Color( 0xcccccc )
    scene.fog = THREE.FogExp2( 0xcccccc, 0.002 )

    geometry = THREE.CylinderGeometry( 0, 10, 30, 4, 1 )
    material = THREE.MeshPhongMaterial( { 'color': 0xffffff, 'flatShading': True } )

    for i in range(500):
        mesh = THREE.Mesh( geometry, material )
        mesh.position.x = ( random.random() - 0.5 ) * 1000
        mesh.position.y = ( random.random() - 0.5 ) * 1000
        mesh.position.z = ( random.random() - 0.5 ) * 1000
        mesh.updateMatrix()
        mesh.matrixAutoUpdate = False
        scene.add( mesh )

    # // lights

    light = THREE.DirectionalLight( 0xffffff )
    light.position.set( 1, 1, 1 )
    scene.add( light )

    light = THREE.DirectionalLight( 0x002288 )
    light.position.set( -1, -1, -1 )
    scene.add( light )

    light = THREE.AmbientLight( 0x222222 )
    scene.add( light )

    # render()


def onWindowResize(event):
    global camera, controls, scene, renderer, cross, container
    height = event.height
    width = event.width

    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize( width, height )

    controls.handleResize(height, width)


def animate():
    global camera, controls, scene, renderer, cross, container

    controls.update()
    render()

def render(event=None):
    global camera, controls, scene, renderer, cross, container
    renderer.render( scene, camera )

def main(argv=None):
    global container
    init()
    return container.loop()


if __name__ == "__main__":
    sys.exit(main())
