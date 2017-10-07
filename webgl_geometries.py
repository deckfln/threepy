"""
        <title>three.js webgl - geometries</title>
"""
import sys
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *


container = None

camera = None
scene = None
renderer = None


def init():
    global container, camera, scene, renderer

    container = pyOpenGL()
    camera = THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 1, 2000 )
    camera.position.y = 400

    scene = THREE.Scene()

    scene.add( THREE.AmbientLight( 0x404040 ) )

    light = THREE.DirectionalLight( 0xffffff )
    light.position.set( 0, 1, 0 )
    scene.add( light )

    map = THREE.TextureLoader().load( 'textures/UV_Grid_Sm.jpg' )
    map.wrapS = map.wrapT = THREE.RepeatWrapping
    map.anisotropy = 16

    material = THREE.MeshLambertMaterial( { "map": map, "side": THREE.DoubleSide } )

    # //

    object = THREE.Mesh( THREE.SphereGeometry( 75, 20, 10 ), material )
    object.position.set( -400, 0, 200 )
    scene.add( object )

    object = THREE.Mesh( THREE.IcosahedronGeometry( 75, 1 ), material )
    object.position.set( -200, 0, 200 )
    scene.add( object )

    object = THREE.Mesh( THREE.OctahedronGeometry( 75, 2 ), material )
    object.position.set( 0, 0, 200 )
    scene.add( object )

    object = THREE.Mesh( THREE.TetrahedronGeometry( 75, 0 ), material )
    object.position.set( 200, 0, 200 )
    scene.add( object )

    # //

    object = THREE.Mesh( THREE.PlaneGeometry( 100, 100, 4, 4 ), material )
    object.position.set( -400, 0, 0 )
    scene.add( object )

    object = THREE.Mesh( THREE.BoxGeometry( 100, 100, 100, 4, 4, 4 ), material )
    object.position.set( -200, 0, 0 )
    scene.add( object )

    object = THREE.Mesh( THREE.CircleGeometry( 50, 20, 0, math.pi * 2 ), material )
    object.position.set( 0, 0, 0 )
    scene.add( object )

    object = THREE.Mesh( THREE.RingGeometry( 10, 50, 20, 5, 0, math.pi * 2 ), material )
    object.position.set( 200, 0, 0 )
    scene.add( object )

    object = THREE.Mesh( THREE.CylinderGeometry( 25, 75, 100, 40, 5 ), material )
    object.position.set( 400, 0, 0 )
    scene.add( object )

    # //

    points = []

    for i in range(50):
        points.append( THREE.Vector2( math.sin( i * 0.2 ) * math.sin( i * 0.1 ) * 15 + 50, ( i - 5 ) * 2 ) )

    object = THREE.Mesh( THREE.LatheGeometry( points, 20 ), material )
    object.position.set( -400, 0, -200 )
    scene.add( object )

    object = THREE.Mesh( THREE.TorusGeometry( 50, 20, 20, 20 ), material )
    object.position.set( -200, 0, -200 )
    scene.add( object )

    object = THREE.Mesh( THREE.TorusKnotGeometry( 50, 10, 50, 20 ), material )
    object.position.set( 0, 0, -200 )
    scene.add( object )

    object = THREE.AxisHelper( 50 )
    object.position.set( 200, 0, -200 )
    scene.add( object )

    object = THREE.ArrowHelper( THREE.Vector3( 0, 1, 0 ), THREE.Vector3( 0, 0, 0 ), 50 )
    object.position.set( 400, 0, -200 )
    scene.add( object )

    # //

    renderer = THREE.pyOpenGLRenderer( { 'antialias': True } )
    renderer.setSize( window.innerWidth, window.innerHeight )

    # //

    container.addEventListener( 'resize', onWindowResize, False )

    
def onWindowResize(event, params):
    global container, camera, scene, renderer
    height = event.height
    width = event.width
    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize(width, height)

# //

def animate(params):
    global container, camera, scene, renderer
    render()

    
def render():
    global container, camera, scene, renderer
    timer = datetime.now().timestamp()

    camera.position.x = math.cos( timer ) * 800
    camera.position.z = math.sin( timer ) * 800

    camera.lookAt( scene.position )

    for obj in scene.children:
        obj.rotation.x = timer * 5
        obj.rotation.y = timer * 2.5

    renderer.render( scene, camera )


def main(argv=None):
    global container
    init()
    container.addEventListener( 'animationRequest', animate)
    return container.loop()


if __name__ == "__main__":
    sys.exit(main())
