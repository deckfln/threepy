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


renderer = None
scene = None
camera = None

sphere = None
uniforms = None

displacement = None
noise = None


def init():
    global camera, scene, renderer, container, displacement, noise, sphere, uniforms

    container = pyOpenGL()

    renderer = THREE.pyOpenGLRenderer( { 'antialias': True } )
    size = renderer.getSize()

    camera = THREE.PerspectiveCamera( 30, size['width'] / size['height'], 1, 10000 )
    camera.position.z = 300

    scene = THREE.Scene()
    scene.background = THREE.Color( 0x050505 )

    uniforms = Uniforms({
        'amplitude': { 'value': 1.0 },
        'color':     { 'value': THREE.Color( 0xff2200 ) },
        'texture':   { 'value': THREE.TextureLoader().load( "textures/water.jpg" ) }
    })

    uniforms.texture.value.wrapS = uniforms.texture.value.wrapT = THREE.RepeatWrapping

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
        'uniforms': uniforms,
        'vertexShader': vertexshader,
        'fragmentShader': fragmentshader
    })


    radius = 50
    segments = 128
    rings = 64

    geometry = THREE.SphereBufferGeometry( radius, segments, rings )

    displacement = Float32Array( geometry.attributes.position.count )
    noise = Float32Array( geometry.attributes.position.count )

    for i in range(len(displacement)):
        noise[ i ] = random.random() * 5

    geometry.addAttribute( 'displacement', THREE.BufferAttribute( displacement, 1 ) )

    sphere = THREE.Mesh( geometry, shaderMaterial )
    scene.add( sphere )

    container.addEventListener( 'resize', onWindowResize, False )

    
def onWindowResize(event, params):
    global camera, scene, renderer, startTime, object, clipMaterial, volumeVisualization, globalClippingPlanes
    height = event.height
    width = event.width
    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize(width, height)


def animate(params):
    render()


def render():
    global camera, scene, renderer, container, displacement, noise, sphere, uniforms

    tim = datetime.now().timestamp()

    sphere.rotation.y = sphere.rotation.z = 0.01 * tim

    uniforms.amplitude.value = 2.5 * math.sin( sphere.rotation.y * 0.125 )
    uniforms.color.value.offsetHSL( 0.0005, 0, 0 )

    for i in range(len(displacement)):
        displacement[ i ] = math.sin( 0.1 * i + tim )

        noise[ i ] += 0.5 * ( 0.5 - random.random() )
        noise[ i ] = _Math.clamp( noise[ i ], -5, 5 )

        displacement[ i ] += noise[ i ]

    sphere.geometry.attributes.displacement.needsUpdate = True

    renderer.render( scene, camera )


def main(argv=None):
    global container
    init()
    container.addEventListener( 'animationRequest', animate)
    return container.loop()


if __name__ == "__main__":
    sys.exit(main())