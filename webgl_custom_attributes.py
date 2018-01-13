"""
        <title>three.js webgl - custom attributes</title>
"""
import sys
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.TrackballControls import *
from THREE.Constants import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.renderer = None
        self.scene = None
        self.camera = None
        self.sphere = None
        self.uniforms = None
        self.displacement = None
        self.noise = None


def init(p):
    p.container = pyOpenGL(p)

    p.renderer = THREE.pyOpenGLRenderer( { 'antialias': True } )

    p.camera = THREE.PerspectiveCamera( 30, window.innerWidth / window.innerHeight, 1, 10000 )
    p.camera.position.z = 300

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0x050505 )

    p.uniforms = Uniforms({
        'amplitude': { 'value': 1.0 },
        'color':     { 'value': THREE.Color( 0xff2200 ) },
        'texture':   { 'value': THREE.TextureLoader().load( "textures/water.jpg" ) }
    })

    p.uniforms.texture.value.wrapS = p.uniforms.texture.value.wrapT = THREE.RepeatWrapping

    vertexshader = """
        uniform float amplitude;

        attribute float displacement;

        varying vec3 vNormal;
        varying vec2 vUv;

        void main() {

            vNormal = normal;
            vUv = ( 0.5 + amplitude ) * uv + vec2( amplitude );

            vec3 newPosition = position + amplitude * normal * vec3( displacement );
            gl_Position = projectionMatrix * modelViewMatrix * vec4( newPosition, 1.0 );

        }
    """

    fragmentshader = """
        varying vec3 vNormal;
        varying vec2 vUv;

        uniform vec3 color;
        uniform sampler2D texture;

        void main() {

            vec3 light = vec3( 0.5, 0.2, 1.0 );
            light = normalize( light );

            float dProd = dot( vNormal, light ) * 0.5 + 0.5;

            vec4 tcolor = texture2D( texture, vUv );
            vec4 gray = vec4( vec3( tcolor.r * 0.3 + tcolor.g * 0.59 + tcolor.b * 0.11 ), 1.0 );

            gl_FragColor = gray * vec4( vec3( dProd ) * vec3( color ), 1.0 );

        }
    """

    shaderMaterial = THREE.ShaderMaterial( {
        'uniforms': p.uniforms,
        'vertexShader': vertexshader,
        'fragmentShader': fragmentshader
    })


    radius = 50
    segments = 128
    rings = 64

    geometry = THREE.SphereBufferGeometry( radius, segments, rings )

    p.displacement = Float32Array( geometry.attributes.position.count )
    p.noise = Float32Array( geometry.attributes.position.count )

    for i in range(len(p.displacement)):
        p.noise[ i ] = random.random() * 5

    geometry.addAttribute( 'displacement', THREE.BufferAttribute( p.displacement, 1 ) )

    p.sphere = THREE.Mesh( geometry, shaderMaterial )
    p.scene.add( p.sphere )

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
    tim = datetime.now().timestamp()

    p.sphere.rotation.y = p.sphere.rotation.z = 0.01 * tim

    p.uniforms.amplitude.value = 2.5 * math.sin( p.sphere.rotation.y * 0.125 )
    p.uniforms.color.value.offsetHSL( 0.0005, 0, 0 )

    for i in range(len(p.displacement)):
        p.displacement[ i ] = math.sin( 0.1 * i + tim )

        p.noise[ i ] += 0.5 * ( 0.5 - random.random() )
        p.noise[ i ] = _Math.clamp( p.noise[ i ], -5, 5 )

        p.displacement[ i ] += p.noise[ i ]

    p.sphere.geometry.attributes.displacement.needsUpdate = True

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())