"""
        <title>three.js webgl - custom attributes [particles]</title>
"""
import math
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.pyOpenGL.pyGUI import *
from THREE.pyOpenGL.widgets.Stats import *


vertexshader = """
    uniform float amplitude;
    attribute float size;
    attribute vec3 customColor;

    varying vec3 vColor;

    void main() {

        vColor = customColor;

        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);

        gl_PointSize = size * (300.0 / -mvPosition.z);

        gl_Position = projectionMatrix * mvPosition;
   }
"""

fragmentshader = """
    uniform vec3 color;
    uniform sampler2D texture;

    varying vec3 vColor;

    void main() {

        gl_FragColor = vec4(color * vColor, 1.0);
        gl_FragColor = gl_FragColor * texture2D(texture, gl_PointCoord);

   }
"""


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.geometry = None
        self.sphere = None
        self.noise = []

def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1, 10000)
    p.camera.position.z = 300

    p.scene = THREE.Scene()

    amount = 100000
    radius = 200

    positions = Float32Array(amount * 3)
    colors = Float32Array(amount * 3)
    sizes = Float32Array(amount)

    vertex = THREE.Vector3()
    color = THREE.Color(0xffffff)

    for i in range(amount):
        vertex.x = (random.random() * 2 - 1) * radius
        vertex.y = (random.random() * 2 - 1) * radius
        vertex.z = (random.random() * 2 - 1) * radius
        vertex.toArray(positions, i * 3)

        if vertex.x < 0:
            color.setHSL(0.5 + 0.1 * (i / amount), 0.7, 0.5)
        else:
            color.setHSL(0.0 + 0.1 * (i / amount), 0.9, 0.5)

        color.toArray(colors, i * 3)

        sizes[i ] = 10

    geometry = THREE.BufferGeometry()
    geometry.addAttribute('position', THREE.BufferAttribute(positions, 3))
    geometry.addAttribute('customColor', THREE.BufferAttribute(colors, 3))
    geometry.addAttribute('size', THREE.BufferAttribute(sizes, 1))

    #

    material = THREE.ShaderMaterial({
        'uniforms': {
            'amplitude': {'value': 1.0},
            'color':     {'value': THREE.Color(0xffffff)},
            'texture':   {'value': THREE.TextureLoader().load("textures/sprites/spark1.png")}
        },
        'vertexShader':   vertexshader,
        'fragmentShader': fragmentshader,

        'blending':       THREE.AdditiveBlending,
        'depthTest':      False,
        'transparent':    True

   })

    #

    p.sphere = THREE.Points(geometry, material)
    p.scene.add(p.sphere)

    #

    p.gui = pyGUI(p.renderer)
    p.gui.add(Stats())


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize(window.innerWidth, window.innerHeight)


def animate(p):
    render(p)
    p.gui.update()


def render(p):
    time = datetime.now().timestamp() * 2

    p.sphere.rotation.z = 0.01 * time

    geometry = p.sphere.geometry
    attributes = geometry.attributes

    for i in range(len(attributes.size.array)):
        attributes.size.array[i ] = 14 + 13 * math.sin(0.1 * i + time)

    attributes.size.needsUpdate = True

    p.renderer.render(p.scene, p.camera)


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
