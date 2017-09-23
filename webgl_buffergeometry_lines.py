"""
    <title>three.js webgl - buffergeometry - lines</title>
"""        
import random
from datetime import datetime
from THREE import *


camera = None
scene = None
renderer = None

mesh = None

WIDTH = 800
HEIGHT = 600


def init():
    global camera, scene, renderer, mesh

    camera = THREE.PerspectiveCamera( 27, WIDTH / HEIGHT, 1, 4000 )
    camera.position.z = 2750

    scene = THREE.Scene()

    segments = 10000

    geometry = THREE.BufferGeometry()
    material = THREE.LineBasicMaterial({ 'vertexColors': THREE.VertexColors })

    positions = Float32Array( segments * 3 )
    colors = Float32Array( segments * 3 )

    r = 800

    for i in range(segments):
        x = random.random() * r - r / 2
        y = random.random() * r - r / 2
        z = random.random() * r - r / 2

        # // positions

        positions[ i * 3 ] = x
        positions[ i * 3 + 1 ] = y
        positions[ i * 3 + 2 ] = z

        # // colors

        colors[ i * 3 ] = ( x / r ) + 0.5
        colors[ i * 3 + 1 ] = ( y / r ) + 0.5
        colors[ i * 3 + 2 ] = ( z / r ) + 0.5

    geometry.addAttribute( 'position', THREE.BufferAttribute( positions, 3 ) )
    geometry.addAttribute( 'color', THREE.BufferAttribute( colors, 3 ) )

    geometry.computeBoundingSphere()

    mesh = THREE.Line( geometry, material )
    scene.add( mesh )

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
    global mesh, renderer
    time = datetime.now().timestamp() * 0.1

    mesh.rotation.x = time * 0.25
    mesh.rotation.y = time * 0.5

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
