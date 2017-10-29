"""
		<title>three.js webgl - buffer geometry custom attributes - particles</title>
"""
from datetime import datetime
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
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

class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None
        self.particleSystem = None
        self.geometry = None


def init(p):
    p.container = pyOpenGL(p)
    p.camera = THREE.PerspectiveCamera( 40, window.innerWidth / window.innerHeight, 1, 10000 )
    p.camera.position.z = 300

    p.scene = THREE.Scene()

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

    p.geometry = THREE.BufferGeometry()

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

    p.geometry.addAttribute( 'position', THREE.BufferAttribute( positions, 3 ) )
    p.geometry.addAttribute( 'customColor', THREE.BufferAttribute( colors, 3 ) )
    p.geometry.addAttribute( 'size', THREE.BufferAttribute( sizes, 1 ) )

    p.particleSystem = THREE.Points( p.geometry, shaderMaterial )

    p.scene.add( p.particleSystem )

    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})

    p.container.addEventListener('resize', onWindowResize, False)


def render(p):
    time = datetime.now().timestamp()

    p.particleSystem.rotation.z = 0.01 * time

    sizes = p.geometry.attributes.size.array

    for i in range(particles):
        sizes[ i ] = 10 * ( 1 + math.sin( 0.1 * i + time ) )

    p.geometry.attributes.size.needsUpdate = True

    p.renderer.render( p.scene, p.camera )


def onWindowResize(event, p):
    windowHalfX = window.innerWidth / 2
    windowHalfY = window.innerHeight / 2

    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize(window.innerWidth, window.innerHeight)


def animate(p):
    render(p)



"""
"""


def main(argv=None):
    global renderer, camera, scene, container
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
