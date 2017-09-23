"""
        <title>three.js webgl - buffergeometry [particles]</title>
"""
import math
import random
from datetime import datetime

from THREE import *


camera = None
scene = None
renderer = None

points = None

WIDTH = 800
HEIGHT = 600

def init():
    global camera, renderer, scene, points

    camera = THREE.PerspectiveCamera( 27, WIDTH / HEIGHT, 5, 3500 )
    camera.position.z = 2750

    scene = THREE.Scene()
    scene.background = THREE.Color( 0x050505 )
    scene.fog = THREE.Fog( 0x050505, 2000, 3500 )

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

    ibp = THREE.InterleavedBuffer( interleaved_buffer_float32, 4 )
    ibc = THREE.InterleavedBuffer( interleaved_buffer_uint8, 16 )

    geometry.addAttribute( 'position', THREE.InterleavedBufferAttribute( ibp, 3, 0, False ) )
    geometry.addAttribute( 'color', THREE.InterleavedBufferAttribute( ibc, 3, 12, True ) )
    # // geometry.computeBoundingSphere()

    # //

    material = THREE.PointsMaterial( { 'size': 15, 'vertexColors': THREE.VertexColors } )

    points = THREE.Points( geometry, material )
    scene.add( points )

    # //
    renderer = pyOpenGLRenderer(None, reshape, render, keyboard, mouse, motion, animate)
    renderer.setPixelRatio( 1 )
    renderer.setSize( WIDTH, HEIGHT )

    renderer.gammaInput = True
    renderer.gammaOutput = True

    return renderer


def animate():
    render()


def render():
    global camera, renderer

    time = datetime.now().timestamp() * 0.1

    points.rotation.x = time * 0.25
    points.rotation.y = time * 0.5

    renderer.render( scene, camera )


def reshape(width, height):
    """window reshape callback."""
    global camera, renderer

    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize(width, height)

    glViewport(0, 0, width, height)


def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        rotating = (state == GLUT_DOWN)
    elif button == GLUT_RIGHT_BUTTON:
        scaling = (state == GLUT_DOWN)


def motion(x1, y1):
    glutPostRedisplay()


def keyboard(c, x=0, y=0):
    """keyboard callback."""

    if c == b'q':
        sys.exit(0)

    glutPostRedisplay()


"""
"""


def main(argv=None):
    global renderer, camera, scene

    renderer = init()
    return renderer.loop()


if __name__ == "__main__":
    sys.exit(main())
