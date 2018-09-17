"""
        <title>three.js webgl - raw shader</title>
"""

import math
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *


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


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None


def init(p):
    p.container = pyOpenGL(p)

    p.camera = THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 1, 3500)
    p.camera.position.z = 2

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0x101010 )

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

    p.mesh = THREE.Mesh( geometry, material )
    p.scene.add( p.mesh )

    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize( window.innerWidth, window.innerHeight )
    p.container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(p):
    render(p)


def render(p):
    time = datetime.now().timestamp() * 0.1

    object = p.scene.children[ 0 ]

    object.rotation.y += 0.01
    object.material.uniforms.time.value += 0.1

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
