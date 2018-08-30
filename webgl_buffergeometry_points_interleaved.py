"""
        <title>three.js webgl - buffergeometry [particles]</title>
"""
import math
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.core.InterleavedBuffer import *


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

    interleaved_buffer_float32 = Float32Array( particles * 4 )
    m = len(interleaved_buffer_float32) * interleaved_buffer_float32.dtype.itemsize
    interleaved_buffer_uint8 = Uint8Array( m )

    color = THREE.Color()

    n = 1000
    n2 = n / 2     # // particles spread in the cube

    for i in range(0, len(interleaved_buffer_float32), 4 ):
        # // positions

        x = random.random() * n - n2
        y = random.random() * n - n2
        z = random.random() * n - n2

        interleaved_buffer_float32[ i + 0 ] = x
        interleaved_buffer_float32[ i + 1 ] = y
        interleaved_buffer_float32[ i + 2 ] = z

        # // colors

        vx = ( x / n ) + 0.5
        vy = ( y / n ) + 0.5
        vz = ( z / n ) + 0.5

        color.setRGB( vx, vy, vz )

        j = ( i + 3 ) * 4

        interleaved_buffer_uint8[ j + 0 ] = int(color.r * 255)
        interleaved_buffer_uint8[ j + 1 ] = int(color.g * 255)
        interleaved_buffer_uint8[ j + 2 ] = int(color.b * 255)
        interleaved_buffer_uint8[ j + 3 ] = 0

    ibp = InterleavedBuffer( interleaved_buffer_float32, 4 )
    ibc = InterleavedBuffer( interleaved_buffer_uint8, 16 )

    geometry.addAttribute( 'position', InterleavedBufferAttribute( ibp, 3, 0, False ) )
    geometry.addAttribute( 'color', InterleavedBufferAttribute( ibc, 3, 12, True ) )
    # // geometry.computeBoundingSphere()

    # //

    material = PointsMaterial( { 'size': 15, 'vertexColors': VertexColors } )

    p.points = Points( geometry, material )
    p.scene.add( p.points )

    # //
    p.renderer = pyOpenGLRenderer({'antialias': True})
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
