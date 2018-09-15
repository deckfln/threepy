"""
    <title>three.js webgl - instancing - lambert shader</title>
"""
import math
from datetime import datetime
import random

from THREE import *
from THREE.scenes.FogExp2 import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.OrbitControls import *
from THREE.renderers.shaders.ShaderLib import _shader_lib as _shader_lib
from extra.CurveExtras import *

# this is a cut-and-paste of the depth shader -- modified to accommodate instancing for this app

ShaderLib['customDepthRGBA'] = _shader_lib(
    ShaderLib['depth'].uniforms,
    """
    // instanced
    #ifdef INSTANCED

        attribute vec3 instanceOffset;
        attribute float instanceScale;

    #endif

    #include <common>
    #include <uv_pars_vertex>
    #include <displacementmap_pars_vertex>
    #include <morphtarget_pars_vertex>
    #include <skinning_pars_vertex>
    #include <logdepthbuf_pars_vertex>
    #include <clipping_planes_pars_vertex>

    void main() {

        #include <uv_vertex>

        #include <skinbase_vertex>

        #ifdef USE_DISPLACEMENTMAP

            #include <beginnormal_vertex>
            #include <morphnormal_vertex>
            #include <skinnormal_vertex>

        #endif

        #include <begin_vertex>

        // instanced
        #ifdef INSTANCED

            transformed *= instanceScale;
            transformed = transformed + instanceOffset;

        #endif

        #include <morphtarget_vertex>
        #include <skinning_vertex>
        #include <displacementmap_vertex>
        #include <project_vertex>
        #include <logdepthbuf_vertex>
        #include <clipping_planes_vertex>

    }
    """,
    ShaderLib['depth'].getFragmentShader()
)

# this is a cut-and-paste of the lambert shader -- modified to accommodate instancing for this app

ShaderLib['lambert'] = _shader_lib(
    ShaderLib['lambert'].uniforms,
    """
    #define LAMBERT

    #ifdef INSTANCED
        attribute vec3 instanceOffset;
        attribute vec3 instanceColor;
        attribute float instanceScale;
    #endif

    varying vec3 vLightFront;

    #ifdef DOUBLE_SIDED

        varying vec3 vLightBack;

    #endif

    #include <common>
    #include <uv_pars_vertex>
    #include <uv2_pars_vertex>
    #include <envmap_pars_vertex>
    #include <bsdfs>
    #include <lights_pars_begin>
    #include <color_pars_vertex>
    #include <fog_pars_vertex>
    #include <morphtarget_pars_vertex>
    #include <skinning_pars_vertex>
    #include <shadowmap_pars_vertex>
    #include <logdepthbuf_pars_vertex>
    #include <clipping_planes_pars_vertex>

    void main() {

        #include <uv_vertex>
        #include <uv2_vertex>
        #include <color_vertex>

        // vertex colors instanced
        #ifdef INSTANCED
            #ifdef USE_COLOR
                vColor.xyz = instanceColor.xyz;
            #endif
        #endif

        #include <beginnormal_vertex>
        #include <morphnormal_vertex>
        #include <skinbase_vertex>
        #include <skinnormal_vertex>
        #include <defaultnormal_vertex>

        #include <begin_vertex>

        // position instanced
        #ifdef INSTANCED
            transformed *= instanceScale;
            transformed = transformed + instanceOffset;
        #endif

        #include <morphtarget_vertex>
        #include <skinning_vertex>
        #include <project_vertex>
        #include <logdepthbuf_vertex>
        #include <clipping_planes_vertex>

        #include <worldpos_vertex>
        #include <envmap_vertex>
        #include <lights_lambert_vertex>
        #include <shadowmap_vertex>
        #include <fog_vertex>

    }
    """,
    ShaderLib['lambert'].fragmentShader
)

#


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None
        self.controls = None


def init(p: Params):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.renderer.shadowMap.enabled = True
    p.renderer.gammaOutput = True

    p.scene = THREE.Scene()

    p.scene.fog = FogExp2(0x000000, 0.004)
    p.renderer.setClearColor(p.scene.fog.color, 1)

    p.camera = THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1, 1000)
    p.camera.position.set(80, 40, 80)

    p.scene.add(p.camera)

    p.controls = OrbitControls(p.camera, p.container)
    p.controls.enableZoom = False
    p.controls.maxPolarAngle = math.pi / 2

    p.scene.add(THREE.AmbientLight(0xffffff, 0.7))

    light = THREE.DirectionalLight(0xffffff, 0.4)
    light.position.set(50, 40, 0)

    light.castShadow = True
    light.shadow.camera.left = - 40
    light.shadow.camera.right = 40
    light.shadow.camera.top = 40
    light.shadow.camera.bottom = - 40
    light.shadow.camera.near = 10
    light.shadow.camera.far = 180

    light.shadow.bias = - 0.001
    light.shadow.mapSize.width = 512
    light.shadow.mapSize.height = 512

    p.scene.add(light)

    # light shadow camera helper
    # light.shadowCameraHelper = THREE.CameraHelper(light.shadow.camera);
    # scene.add(light.shadowCameraHelper);

    # instanced buffer geometry

    geometry = THREE.InstancedBufferGeometry()
    geometry.copy(THREE.TorusBufferGeometry(2, 0.5, 8, 128))

    INSTANCES = 256

    knot = TorusKnot(10)
    positions = knot.getSpacedPoints(INSTANCES)

    offsets = Float32Array(INSTANCES * 3)  # xyz
    colors = Float32Array(INSTANCES * 3)   # rgb
    scales = Float32Array(INSTANCES * 1)   # s

    for i in range(INSTANCES):
        index = 3 * i

        # per-instance position offset
        offsets[index] = positions[i].x
        offsets[index + 1] = positions[i].y
        offsets[index + 2] = positions[i].z

        # per-instance color tint - optional
        colors[index] = 1
        colors[index + 1] = 1
        colors[index + 2] = 1

        # per-instance scale variation
        scales[i] = 1 + 0.5 * math.sin(32 * math.pi * i / INSTANCES)

    geometry.addAttribute('instanceOffset', THREE.InstancedBufferAttribute(offsets, 3))
    geometry.addAttribute('instanceColor', THREE.InstancedBufferAttribute(colors, 3))
    geometry.addAttribute('instanceScale', THREE.InstancedBufferAttribute(scales, 1))

    # material

    def _load(texture):
        texture.mapping = THREE.SphericalReflectionMapping
        texture.encoding = THREE.sRGBEncoding
        if p.mesh:
            p.mesh.material.needsUpdate = True

    envMap = THREE.TextureLoader().load('textures/metal.jpg', _load)

    material = THREE.MeshLambertMaterial({
        'color': 0xffb54a,
        'envMap': envMap,
        'combine': THREE.MultiplyOperation,
        'reflectivity': 0.8,
        'vertexColors': THREE.VertexColors,
        'fog': True
    })

    material.defines = material.defines or {}
    material.defines['INSTANCED'] = ""

    # custom depth material - required for instanced shadows

    shader = THREE.ShaderLib['customDepthRGBA']

    uniforms = THREE.UniformsUtils.clone(shader.uniforms)

    customDepthMaterial = THREE.ShaderMaterial({
        'defines': {
            'INSTANCED': "",
            'DEPTH_PACKING': THREE.RGBADepthPacking
        },
        'uniforms': uniforms,
        'vertexShader': shader.vertexShader,
        'fragmentShader': shader.fragmentShader
    })

    #

    p.mesh = THREE.Mesh(geometry, material)
    p.mesh.scale.set(1, 1, 2)
    p.mesh.castShadow = True
    p.mesh.receiveShadow = True
    p.mesh.customDepthMaterial = customDepthMaterial
    p.mesh.frustumCulled = False

    p.scene.add(p.mesh)

    #

    ground = THREE.Mesh(
        THREE.PlaneBufferGeometry(800, 800).rotateX(- math.pi / 2),
        THREE.MeshPhongMaterial({'color': 0x888888})
    )
    ground.position.set(0, - 40, 0)
    ground.receiveShadow = True

    p.scene.add(ground)


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize(window.innerWidth, window.innerHeight)


def animate(p: Params):
    p.mesh.rotation.y += 0.005

    p.renderer.render(p.scene, p.camera)


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
