"""
        <title>three.js webgl - geometries</title>
"""
import sys
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.helpers.AxesHelper import *


class Params:
    def __init__(self):
        self.container = None
        self.camera = None
        self.scene = None
        self.renderer = None


def init(p):
    p.container = pyOpenGL(p)
    p.camera = THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 1, 2000 )
    p.camera.position.y = 400

    p.scene = THREE.Scene()

    p.scene.add( THREE.AmbientLight( 0x404040 ) )

    light = THREE.DirectionalLight( 0xffffff )
    light.position.set( 0, 1, 0 )
    p.scene.add( light )

    map = THREE.TextureLoader().load( 'textures/UV_Grid_Sm.jpg' )
    map.wrapS = map.wrapT = THREE.RepeatWrapping
    map.anisotropy = 16

    material = THREE.MeshLambertMaterial( { "map": map, "side": THREE.DoubleSide } )

    # //

    object = THREE.Mesh( THREE.SphereGeometry( 75, 20, 10 ), material )
    object.position.set( -400, 0, 200 )
    p.scene.add( object )

    object = THREE.Mesh( THREE.IcosahedronGeometry( 75, 1 ), material )
    object.position.set( -200, 0, 200 )
    p.scene.add( object )

    object = THREE.Mesh( THREE.OctahedronGeometry( 75, 2 ), material )
    object.position.set( 0, 0, 200 )
    p.scene.add( object )

    object = THREE.Mesh( THREE.TetrahedronGeometry( 75, 0 ), material )
    object.position.set( 200, 0, 200 )
    p.scene.add( object )

    # //

    object = THREE.Mesh( THREE.PlaneGeometry( 100, 100, 4, 4 ), material )
    object.position.set( -400, 0, 0 )
    p.scene.add( object )

    object = THREE.Mesh( THREE.BoxGeometry( 100, 100, 100, 4, 4, 4 ), material )
    object.position.set( -200, 0, 0 )
    p.scene.add( object )

    object = THREE.Mesh( THREE.CircleGeometry( 50, 20, 0, math.pi * 2 ), material )
    object.position.set( 0, 0, 0 )
    p.scene.add( object )

    object = THREE.Mesh( THREE.RingGeometry( 10, 50, 20, 5, 0, math.pi * 2 ), material )
    object.position.set( 200, 0, 0 )
    p.scene.add( object )

    object = THREE.Mesh( THREE.CylinderGeometry( 25, 75, 100, 40, 5 ), material )
    object.position.set( 400, 0, 0 )
    p.scene.add( object )

    # //

    points = []

    for i in range(50):
        points.append( THREE.Vector2( math.sin( i * 0.2 ) * math.sin( i * 0.1 ) * 15 + 50, ( i - 5 ) * 2 ) )

    object = THREE.Mesh( THREE.LatheGeometry( points, 20 ), material )
    object.position.set( -400, 0, -200 )
    p.scene.add( object )

    object = THREE.Mesh( THREE.TorusGeometry( 50, 20, 20, 20 ), material )
    object.position.set( -200, 0, -200 )
    p.scene.add( object )

    object = THREE.Mesh( THREE.TorusKnotGeometry( 50, 10, 50, 20 ), material )
    object.position.set( 0, 0, -200 )
    p.scene.add( object )

    object = AxesHelper( 50 )
    object.position.set( 200, 0, -200 )
    p.scene.add( object )

    object = THREE.ArrowHelper( THREE.Vector3( 0, 1, 0 ), THREE.Vector3( 0, 0, 0 ), 50 )
    object.position.set( 400, 0, -200 )
    p.scene.add( object )

    # //

    p.renderer = THREE.pyOpenGLRenderer( { 'antialias': True } )
    p.renderer.setSize( window.innerWidth, window.innerHeight )

    # //

    p.container.addEventListener( 'resize', onWindowResize, False )

    
def onWindowResize(event, p):
    height = event.height
    width = event.width
    p.camera.aspect = width / height
    p.camera.updateProjectionMatrix()

    p.renderer.setSize(width, height)


def animate(p):
    render(p)

    
def render(p):
    timer = datetime.now().timestamp() * 0.1

    p.camera.position.x = math.cos( timer ) * 800
    p.camera.position.z = math.sin( timer ) * 800

    p.camera.lookAt( p.scene.position )

    for obj in p.scene.children:
        obj.rotation.x = timer * 5
        obj.rotation.y = timer * 2.5

        p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
