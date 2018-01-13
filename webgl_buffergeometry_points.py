"""
        <title>three.js webgl - buffergeometry [particles]</title>
"""        
import math
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.points = None


def init(p):
    p.container = pyOpenGL(p)

    p.camera = THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 1, 3500)
    p.camera.position.z = 2750

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0x050505 )
    p.scene.fog = THREE.Fog( 0x050505, 2000, 3500 )

    # //

    particles = 500000

    geometry = THREE.BufferGeometry()

    positions = Float32Array( particles * 3 )
    colors = Float32Array( particles * 3 )

    color = THREE.Color()

    n = 1000
    n2 = n / 2  # // particles spread in the cube

    for i in range(0, len(positions), 3 ):
        # // positions

        x = random.random() * n - n2
        y = random.random() * n - n2
        z = random.random() * n - n2

        positions[ i ]     = x
        positions[ i + 1 ] = y
        positions[ i + 2 ] = z

        # // colors

        vx = ( x / n ) + 0.5
        vy = ( y / n ) + 0.5
        vz = ( z / n ) + 0.5

        color.setRGB( vx, vy, vz )

        colors[ i ]     = color.r
        colors[ i + 1 ] = color.g
        colors[ i + 2 ] = color.b

    geometry.addAttribute( 'position', THREE.BufferAttribute( positions, 3 ) )
    geometry.addAttribute( 'color', THREE.BufferAttribute( colors, 3 ) )

    geometry.computeBoundingSphere()

    # //

    material = THREE.PointsMaterial( { 'size': 15, 'vertexColors': THREE.VertexColors } )

    p.points = THREE.Points( geometry, material )
    p.scene.add( p.points )

    # //

    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize( window.innerWidth, window.innerHeight )
    p.container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(p):
    render(p)


def render(p):
    time = datetime.now().timestamp()

    p.points.rotation.x = time * 0.25
    p.points.rotation.y = time * 0.5

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
