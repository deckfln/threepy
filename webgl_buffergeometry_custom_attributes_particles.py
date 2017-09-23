"""
		<title>three.js webgl - buffer geometry custom attributes - particles</title>
"""
from datetime import datetime
from THREE import *
import random


vertexshader = """
attribute float size;
attribute vec3 customColor;

varying vec3 vColor;

void main() {
    vColor = customColor;
    vec4 mvPosition = modelViewMatrix * vec4( position, 1.0 );
    gl_PointSize = size * ( 300.0 / -mvPosition.z );
    gl_Position = projectionMatrix * mvPosition;
}
"""

fragmentshader = """
uniform vec3 color;
uniform sampler2D texture;

varying vec3 vColor;

void main() {
    gl_FragColor = vec4( color * vColor, 1.0 );
    gl_FragColor = gl_FragColor * texture2D( texture, gl_PointCoord );
}
"""


particles = 100000

WIDTH = 640
HEIGHT = 480
camera = None
scene=None
renderer=None
mesh = None
particleSystem = None
geometry = None


def init():
    global camera, renderer, particleSystem, geometry, scene

    camera = THREE.PerspectiveCamera( 40, WIDTH / HEIGHT, 1, 10000 )
    camera.position.z = 300

    scene = THREE.Scene()

    uniforms = {
        'color':     { 'value': THREE.Color( 0xffffff ) },
        'texture':   { 'value': THREE.TextureLoader().load( "textures/sprites/spark1.png" ) }

    }

    shaderMaterial = THREE.ShaderMaterial( {
        'uniforms':       uniforms,
        'vertexShader':   vertexshader,
        'fragmentShader': fragmentshader,

        'blending':       THREE.AdditiveBlending,
        'depthTest':      False,
        'transparent':    True
    })

    radius = 200

    geometry = THREE.BufferGeometry()

    positions = Float32Array( particles * 3 )
    colors = Float32Array( particles * 3 )
    sizes = Float32Array( particles )

    color = THREE.Color()

    i3 = 0
    for i in range(particles):
        positions[ i3 + 0 ] = ( random.random() * 2 - 1 ) * radius
        positions[ i3 + 1 ] = ( random.random() * 2 - 1 ) * radius
        positions[ i3 + 2 ] = ( random.random() * 2 - 1 ) * radius

        color.setHSL( i / particles, 1.0, 0.5 )

        colors[ i3 + 0 ] = color.r
        colors[ i3 + 1 ] = color.g
        colors[ i3 + 2 ] = color.b

        sizes[ i ] = 20

        i3 += 3

    geometry.addAttribute( 'position', THREE.BufferAttribute( positions, 3 ) )
    geometry.addAttribute( 'customColor', THREE.BufferAttribute( colors, 3 ) )
    geometry.addAttribute( 'size', THREE.BufferAttribute( sizes, 1 ) )

    particleSystem = THREE.Points( geometry, shaderMaterial )

    scene.add( particleSystem )

    renderer = pyOpenGLRenderer(None, reshape, render, keyboard, mouse, motion, animate)
    renderer.setPixelRatio( 1 )
    renderer.setSize( WIDTH, HEIGHT )

    return renderer


def render():
    global camera, scene, renderer, particleSystem
    time = datetime.now().timestamp()

    particleSystem.rotation.z = 0.01 * time

    sizes = geometry.attributes.size.array

    for i in range(particles):
        sizes[ i ] = 10 * ( 1 + math.sin( 0.1 * i + time ) )

    geometry.attributes.size.needsUpdate = True

    renderer.render( scene, camera )

def reshape(width, height):
    """window reshape callback."""
    global camera, renderer

    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize(width, height)

    glViewport(0, 0, width, height)


def animate():
    render()


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
