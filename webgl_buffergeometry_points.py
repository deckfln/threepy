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
    global camera, scene, renderer, points
    
    camera = THREE.PerspectiveCamera( 27, WIDTH / HEIGHT, 5, 3500 )
    camera.position.z = 2750

    scene = THREE.Scene()
    scene.background = THREE.Color( 0x050505 )
    scene.fog = THREE.Fog( 0x050505, 2000, 3500 )

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
    global renderer, scene, camera
    
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
