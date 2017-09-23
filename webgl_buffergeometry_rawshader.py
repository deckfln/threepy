"""
        <title>three.js webgl - raw shader</title>
"""

import math
import random
from datetime import datetime

from THREE import *

vertexShader = """
precision mediump float;
precision mediump int;

uniform mat4 modelViewMatrix; // optional
uniform mat4 projectionMatrix; // optional

attribute vec3 position;
attribute vec4 color;

varying vec3 vPosition;
varying vec4 vColor;

void main()    {

    vPosition = position;
    vColor = color;

    gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );

}
"""

fragmentShader = """
precision mediump float;
precision mediump int;

uniform float time;

varying vec3 vPosition;
varying vec4 vColor;

void main()    {

    vec4 color = vec4( vColor );
    color.r += sin( vPosition.x * 10.0 + time ) * 0.5;

    gl_FragColor = color;

}
"""

camera = None
scene = None
renderer = None

WIDTH = 800
HEIGHT = 600


def init():
    global camera, scene, renderer
    camera = THREE.PerspectiveCamera( 50, WIDTH / HEIGHT, 1, 10 )
    camera.position.z = 2

    scene = THREE.Scene()
    scene.background = THREE.Color( 0x101010 )

    # // geometry

    triangles = 500

    geometry = THREE.BufferGeometry()

    vertices = Float32Array( triangles * 3 * 3 )

    for i in range(0, triangles * 3 * 3, 3 ):
        vertices[ i     ] = random.random() - 0.5
        vertices[ i + 1 ] = random.random() - 0.5
        vertices[ i + 2 ] = random.random() - 0.5

    geometry.addAttribute( 'position', THREE.BufferAttribute( vertices, 3 ) )

    colors = Uint8Array( triangles * 3 * 4 )

    for i in range(0, triangles * 3 * 4, 4 ):
        colors[ i     ] = random.random() * 255
        colors[ i + 1 ] = random.random() * 255
        colors[ i + 2 ] = random.random() * 255
        colors[ i + 3 ] = random.random() * 255

    geometry.addAttribute( 'color', THREE.BufferAttribute( colors, 4, True ) )

    # // material

    material = THREE.RawShaderMaterial( {
        'uniforms': {
            'time': { 'value': 1.0 }
        },
        'vertexShader': vertexShader,
        'fragmentShader': fragmentShader,
        'side': THREE.DoubleSide,
        'transparent': True
    } )

    mesh = THREE.Mesh( geometry, material )
    scene.add( mesh )

    renderer = pyOpenGLRenderer(None, reshape, render, keyboard, mouse, motion, animate)
    renderer.setPixelRatio( 1 )
    renderer.setSize( WIDTH, HEIGHT )

    renderer.gammaInput = True
    renderer.gammaOutput = True

    return renderer


def animate():
    render()


def render():
    global camera, scene, renderer

    time = datetime.now().timestamp() * 0.001

    object = scene.children[ 0 ]

    object.rotation.y += 0.01
    object.material.uniforms.time.value += 0.1

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
