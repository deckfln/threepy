"""
        <title>three.js webgl - geometry - dynamic</title>
"""
import random
import math
import sys
from datetime import datetime
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.FirstPersonControls import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None
        self.texture = None
        self.geometry = None
        self.material = None
        self.worldWidth = 128
        self.worldDepth = 128
        self.worldHalfWidth = self.worldWidth / 2
        self.worldHalfDepth = self.worldDepth / 2
        self.clock = THREE.Clock()
        self.controls = None


def init(p):
    p.container = pyOpenGL(p)

    p.camera = THREE.PerspectiveCamera( 60, window.innerWidth / window.innerHeight, 1, 20000 )
    p.camera.position.y = 200

    p.controls = FirstPersonControls( p.camera, p.container )

    p.controls.movementSpeed = 500
    p.controls.lookSpeed = 0.1

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0xaaccff )
    p.scene.fog = THREE.FogExp2( 0xaaccff, 0.0007 )

    p.geometry = THREE.PlaneBufferGeometry( 20000, 20000, p.worldWidth - 1, p.worldDepth - 1 )
    p.geometry.rotateX( - math.pi / 2 )

    positions = p.geometry.attributes.position.array
    for i in range(1, len(positions), 3):
        positions[i] = 35 * math.sin( i / 2 )

    p.texture = THREE.TextureLoader().load( "textures/crate.gif" )
    p.texture.wrapS = p.texture.wrapT = THREE.RepeatWrapping
    p.texture.repeat.set( 5, 5 )

    p.material = THREE.MeshBasicMaterial( { 'color': 0x0044ff, 'map': p.texture, 'wireframe': False} )

    p.mesh = THREE.Mesh( p.geometry, p.material )
    p.scene.add( p.mesh )

    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize( window.innerWidth, window.innerHeight )

    # //

    p.container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event, p):
    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )

    p.controls.handleResize(window.innerWidth, window.innerHeight)


def animate(p):
    render(p)


def render(p):
    delta = p.clock.getDelta()
    time = p.clock.getElapsedTime() * 5000

    positions = p.geometry.attributes.position.array
    k = 0
    for i in range(1, len(positions), 3):
        positions[i] = 35 * math.sin( k / 5 + ( time + k ) / 7 )
        k += 1

    p.mesh.geometry.attributes.position.needsUpdate = True

    p.controls.update( delta * 500)
    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
