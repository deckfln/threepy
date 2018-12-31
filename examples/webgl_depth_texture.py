"""
<title>three.js webgl - Depth Texture</title>
Created by <a href="http://twitter.com/mattdesl" target="_blank" rel="noopener">@mattdesl</a>.
"""
import math
import random
import math
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.pyOpenGL.pyGUI import *
from THREE.pyOpenGL.widgets.Stats import *
from THREE.controls.OrbitControls import *
from THREE.textures.DepthTexture import *


post_vert = """
varying vec2 vUv;

void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
"""


post_frag = """
#include <packing>

varying vec2 vUv;
uniform sampler2D tDiffuse;
uniform sampler2D tDepth;
uniform float cameraNear;
uniform float cameraFar;


float readDepth(sampler2D depthSampler, vec2 coord) {
    float fragCoordZ = texture2D(depthSampler, coord).x;
    float viewZ = perspectiveDepthToViewZ(fragCoordZ, cameraNear, cameraFar);
    return viewZToOrthographicDepth(viewZ, cameraNear, cameraFar);
}

void main() {
    //vec3 diffuse = texture2D(tDiffuse, vUv).rgb
    float depth = readDepth(tDepth, vUv);

    gl_FragColor.rgb = 1.0 - vec3(depth);
    gl_FragColor.a = 1.0;
}
"""

class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.geometry = None
        self.target = None
        self.postScene = None
        self.postCamera = None
        self.supportsExtension = True


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    #

    p.gui = pyGUI(p.renderer)
    p.gui.add(Stats())

    p.camera = THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.01, 50)
    p.camera.position.z = 4

    p.controls = OrbitControls(p.camera, p.container)
    p.controls.enableDamping = True
    p.controls.dampingFactor = 0.25
    p.controls.rotateSpeed = 0.35

    # Create a multi render target with Float buffers
    p.target = THREE.pyOpenGLRenderTarget(window.innerWidth, window.innerHeight)
    p.target.texture.format = THREE.RGBFormat
    p.target.texture.minFilter = THREE.NearestFilter
    p.target.texture.magFilter = THREE.NearestFilter
    p.target.texture.generateMipmaps = False
    p.target.stencilBuffer = False
    p.target.depthBuffer = True
    p.target.depthTexture = DepthTexture()
    p.target.depthTexture.type = THREE.UnsignedShortType

    # Our scene
    p.scene = THREE.Scene()
    setupScene(p)

    # Setup post-processing step
    setupPost(p)

    onWindowResize(None, p)

    
def setupPost (p):
    # Setup post processing stage
    p.postCamera = THREE.OrthographicCamera(- 1, 1, 1, - 1, 0, 1)
    p.postMaterial = THREE.ShaderMaterial({
        'vertexShader': post_vert,
        'fragmentShader': post_frag,
        'uniforms': {
            'cameraNear': {'value': p.camera.near},
            'cameraFar':  {'value': p.camera.far},
            'tDiffuse':   {'value': p.target.texture},
            'tDepth':     {'value': p.target.depthTexture}
        }
    })
    postPlane = THREE.PlaneBufferGeometry(2, 2)
    postQuad = THREE.Mesh(postPlane, p.postMaterial)
    p.postScene = THREE.Scene()
    p.postScene.add(postQuad)


def setupScene (p):
    #diffuse = THREE.TextureLoader().load('textures/brick_diffuse.jpg')
    #diffuse.wrapS = diffuse.wrapT = THREE.RepeatWrapping

    # Setup some geometries
    geometry = THREE.TorusKnotBufferGeometry(1, 0.3, 128, 64)
    material = THREE.MeshBasicMaterial({ 'color': 'blue' })

    count = 50
    scale = 5

    for i in range(count):
        r = random.random() * 2.0 * math.pi
        z = (random.random() * 2.0) - 1.0
        zScale = math.sqrt(1.0 - z * z) * scale

        mesh = THREE.Mesh(geometry, material)
        mesh.position.set(
            math.cos(r) * zScale,
            math.sin(r) * zScale,
            z * scale
       )
        mesh.rotation.set(random.random(), random.random(), random.random())
        p.scene.add(mesh)


def onWindowResize(event, p):
    aspect = window.innerWidth / window.innerHeight
    p.camera.aspect = aspect
    p.camera.updateProjectionMatrix()

    dpr = p.renderer.getPixelRatio()
    p.target.setSize(window.innerWidth * dpr, window.innerHeight * dpr)
    p.renderer.setSize(window.innerWidth, window.innerHeight)


def animate(p):
    # render scene into target
    p.renderer.render(p.scene, p.camera, p.target)

    # render post FX
    p.renderer.render(p.postScene, p.postCamera)

    p.gui.update()

    
def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
