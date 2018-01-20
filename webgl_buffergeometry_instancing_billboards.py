"""
    <title>three.js webgl - instanced particles - billboards - colors</title>
"""
import random

from THREE import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.TrackballControls import *


vshader = """
        precision highp float;
        uniform mat4 modelViewMatrix;
        uniform mat4 projectionMatrix;
        uniform float time;

        attribute vec3 position;
        attribute vec2 uv;
        attribute vec3 translate;

        varying vec2 vUv;
        varying float vScale;

        void main() {

            vec4 mvPosition = modelViewMatrix * vec4( translate, 1.0 );
            vec3 trTime = vec3(translate.x + time,translate.y + time,translate.z + time);
            float scale =  sin( trTime.x * 2.1 ) + sin( trTime.y * 3.2 ) + sin( trTime.z * 4.3 );
            vScale = scale;
            scale = scale * 10.0 + 10.0;
            mvPosition.xyz += position * scale;
            vUv = uv;
            gl_Position = projectionMatrix * mvPosition;

        }
"""        

fshader = """
        precision highp float;

        uniform sampler2D map;

        varying vec2 vUv;
        varying float vScale;

        // HSL to RGB Convertion helpers
        vec3 HUEtoRGB(float H){
            H = mod(H,1.0);
            float R = abs(H * 6.0 - 3.0) - 1.0;
            float G = 2.0 - abs(H * 6.0 - 2.0);
            float B = 2.0 - abs(H * 6.0 - 4.0);
            return clamp(vec3(R,G,B),0.0,1.0);
        }

        vec3 HSLtoRGB(vec3 HSL){
            vec3 RGB = HUEtoRGB(HSL.x);
            float C = (1.0 - abs(2.0 * HSL.z - 1.0)) * HSL.y;
            return (RGB - 0.5) * C + HSL.z;
        }

        void main() {
            vec4 diffuseColor = texture2D( map, vUv );
            gl_FragColor = vec4( diffuseColor.xyz * HSLtoRGB(vec3(vScale/5.0, 1.0, 0.5)), diffuseColor.w );

            if ( diffuseColor.w < 0.5 ) discard;
        }
"""        


class Params:
    def __init__(self):
        self.container = None
        self.camera = None
        self.scene = None
        self.renderer = None
        self.geometry = None
        self.material = None
        self.mesh = None
        self.clock = THREE.Clock()


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 1, 5000 )
    p.camera.position.z = 1400

    p.scene = THREE.Scene()

    p.geometry = THREE.InstancedBufferGeometry()
    p.geometry.copy( THREE.CircleBufferGeometry( 1, 6 ) )

    particleCount = 75000

    translateArray = Float32Array( particleCount * 3 )

    i3 = 0
    for i in range(particleCount):
        translateArray[ i3 + 0 ] = random.random() * 2 - 1
        translateArray[ i3 + 1 ] = random.random() * 2 - 1
        translateArray[ i3 + 2 ] = random.random() * 2 - 1
        i3 += 3

    p.geometry.addAttribute( "translate", THREE.InstancedBufferAttribute( translateArray, 3, 1 ) )

    p.material = THREE.RawShaderMaterial( {
        'uniforms': {
            'map': UniformValue(THREE.TextureLoader().load( "textures/sprites/circle.png" ) ),
            'time': UniformValue(1.0)
        },
        'vertexShader': vshader,
        'fragmentShader': fshader,
        'depthTest': True,
        'depthWrite': True
    } )

    p.mesh = THREE.Mesh( p.geometry, p.material )
    p.mesh.scale.set( 500, 500, 500 )
    p.scene.add( p.mesh )

    p.clock.start()


def animate(p):
    render(p)


def render(p):
    time = p.clock.getElapsedTime()

    p.material.uniforms.time.value = time*.5

    p.mesh.rotation.x = time * 0.2
    p.mesh.rotation.y = time * 0.4

    p.renderer.render( p.scene, p.camera )


def onWindowResize(event, p):
    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
