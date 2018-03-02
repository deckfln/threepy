"""
    <title>three.js webgl - postprocessing - godrays</title>
    <a href="http:#threejs.org" target="_blank" rel="noopener">three.js</a> - webgl god-rays example - tree by <a href="http:#www.turbosquid.com/3d-models/free-tree-3d-model/592617" target="_blank" rel="noopener">stanloshka</a>
"""

from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.loaders.OBJLoader import *
import shaders.ShaderGodRays as ShaderGodRays


class _postProcessing:
    def __init__(self):
        self.enabled = True
        self.scene = None
        self.camera = None
        self.rtTextureColors = None
        self.rtTextureDepth = None
        self.rtTextureGodRays1 = None
        self.rtTextureGodRays2 = None
        self.godrayGenUniforms = None
        self.materialGodraysGenerate = None


class Params:
    def __init__(self):
        self.container = None
        self.camera = None
        self.scene = None
        self.renderer = None
        self.materialDepth = None
        self.sphereMesh = None

        self.sunPosition = THREE.Vector3(0, 1000, -1000)
        self.screenSpacePosition = THREE.Vector3()

        self.mouseX = 0
        self.mouseY = 0

        self.windowHalfX = window.innerWidth / 2
        self.windowHalfY = window.innerHeight / 2

        self.postprocessing = _postProcessing()

        self.orbitRadius = 200

        self.bgColor = 0x000511
        self.sunColor = 0xffee00

        self.debug_scene = None
        self.debug = None


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.container.addEventListener('mousemove', onDocumentMouseMove, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 1, 3000)
    p.camera.position.z = 200

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color(p.bgColor)

    #

    p.materialDepth = THREE.MeshDepthMaterial()

    materialScene = THREE.MeshBasicMaterial({'color': 0x000000})

    # tree

    loader = OBJLoader()
    object = loader.load("models/obj/tree.obj")

    object.material = materialScene
    object.position.set(0, -150, -150)
    object.scale.multiplyScalar(400)
    p.scene.add(object)

    # sphere

    geo = THREE.SphereGeometry(1, 20, 10)
    p.sphereMesh = THREE.Mesh(geo, materialScene)
    p.sphereMesh.scale.multiplyScalar(20)
    p.scene.add(p.sphereMesh)

    #

    p.renderer.autoClear = False

    #

    initPostprocessing(p)


def onDocumentMouseMove(event, p):
    p.mouseX = event.clientX - p.windowHalfX
    p.mouseY = event.clientY - p.windowHalfY


def initPostprocessing(p):
    p.postprocessing.scene = THREE.Scene()

    p.postprocessing.camera = THREE.OrthographicCamera(window.innerWidth / - 2, window.innerWidth / 2,  window.innerHeight / 2, window.innerHeight / - 2, -10000, 10000)
    p.postprocessing.camera.position.z = 100

    p.postprocessing.scene.add(p.postprocessing.camera)

    pars = {'minFilter': THREE.LinearFilter, 'magFilter': THREE.LinearFilter, 'format': THREE.RGBFormat}
    p.postprocessing.rtTextureColors = THREE.pyOpenGLRenderTarget(window.innerWidth, window.innerHeight, pars)

    # Switching the depth formats to luminance from rgb doesn't seem to work. I didn't
    # investigate further for now.
    # pars.format = THREE.LuminanceFormat

    # I would have this quarter size and use it as one of the ping-pong render
    # targets but the aliasing causes some temporal flickering

    p.postprocessing.rtTextureDepth = THREE.pyOpenGLRenderTarget(window.innerWidth, window.innerHeight, pars)

    # Aggressive downsize god-ray ping-pong render targets to minimize cost

    w = window.innerWidth / 4.0
    h = window.innerHeight / 4.0
    p.postprocessing.rtTextureGodRays1 = THREE.pyOpenGLRenderTarget(w, h, pars)
    p.postprocessing.rtTextureGodRays2 = THREE.pyOpenGLRenderTarget(w, h, pars)

    # god-ray shaders

    godraysGenShader = ShaderGodRays.ShaderGodRays["godrays_generate"]
    p.postprocessing.godrayGenUniforms = THREE.UniformsUtils.clone(godraysGenShader.uniforms)
    p.postprocessing.materialGodraysGenerate = THREE.ShaderMaterial({
        'uniforms': p.postprocessing.godrayGenUniforms,
        'vertexShader': godraysGenShader.vertexShader,
        'fragmentShader': godraysGenShader.fragmentShader
   })

    godraysCombineShader = ShaderGodRays.ShaderGodRays["godrays_combine"]
    p.postprocessing.godrayCombineUniforms = THREE.UniformsUtils.clone(godraysCombineShader.uniforms)
    p.postprocessing.materialGodraysCombine = THREE.ShaderMaterial({
        'uniforms': p.postprocessing.godrayCombineUniforms,
        'vertexShader': godraysCombineShader.vertexShader,
        'fragmentShader': godraysCombineShader.fragmentShader
   })

    godraysFakeSunShader = ShaderGodRays.ShaderGodRays["godrays_fake_sun"]
    p.postprocessing.godraysFakeSunUniforms = THREE.UniformsUtils.clone(godraysFakeSunShader.uniforms)
    p.postprocessing.materialGodraysFakeSun = THREE.ShaderMaterial({
        'uniforms': p.postprocessing.godraysFakeSunUniforms,
        'vertexShader': godraysFakeSunShader.vertexShader,
        'fragmentShader': godraysFakeSunShader.fragmentShader
   })

    p.postprocessing.godraysFakeSunUniforms.bgColor.value.setHex(p.bgColor)
    p.postprocessing.godraysFakeSunUniforms.sunColor.value.setHex(p.sunColor)

    p.postprocessing.godrayCombineUniforms.fGodRayIntensity.value = 0.75

    p.postprocessing.quad = THREE.Mesh(
        THREE.PlaneBufferGeometry(window.innerWidth, window.innerHeight),
        p.postprocessing.materialGodraysGenerate
   )
    p.postprocessing.quad.position.z = -9900
    p.postprocessing.scene.add(p.postprocessing.quad)


def animate(p):
    render(p)


def render(p):
    time = datetime.now().timestamp() * 0.1

    p.sphereMesh.position.x = p.orbitRadius * math.cos(time)
    p.sphereMesh.position.z = p.orbitRadius * math.sin(time) - 100

    p.camera.position.x += (p.mouseX - p.camera.position.x) * 0.036
    p.camera.position.y += (- (p.mouseY) - p.camera.position.y) * 0.036

    p.camera.lookAt(p.scene.position)

    if p.postprocessing.enabled:
        p.renderer.clear()
        # Find the screenspace position of the sun

        p.screenSpacePosition.copy(p.sunPosition).project(p.camera)

        p.screenSpacePosition.x = (p.screenSpacePosition.x + 1) / 2
        p.screenSpacePosition.y = (p.screenSpacePosition.y + 1) / 2

        # Give it to the god-ray and sun shaders

        p.postprocessing.godrayGenUniforms.vSunPositionScreenSpace.value.x = p.screenSpacePosition.x
        p.postprocessing.godrayGenUniforms.vSunPositionScreenSpace.value.y = p.screenSpacePosition.y

        p.postprocessing.godraysFakeSunUniforms.vSunPositionScreenSpace.value.x = p.screenSpacePosition.x
        p.postprocessing.godraysFakeSunUniforms.vSunPositionScreenSpace.value.y = p.screenSpacePosition.y

        # -- Draw sky and sun --

        # Clear colors and depths, will clear to sky color

        p.renderer.clearTarget(p.postprocessing.rtTextureColors, True, True, False)

        # Sun render. Runs a shader that gives a brightness based on the screen
        # space distance to the sun. Not very efficient, so i make a scissor
        # rectangle around the suns position to avoid rendering surrounding pixels.

        sunsqH = 0.74 * window.innerHeight	 # 0.74 depends on extent of sun from shader
        sunsqW = 0.74 * window.innerHeight	 # both depend on height because sun is aspect-corrected

        p.screenSpacePosition.x *= window.innerWidth
        p.screenSpacePosition.y *= window.innerHeight

        p.renderer.setScissorTest(True)
        p.renderer.setScissor(p.screenSpacePosition.x - sunsqW / 2, p.screenSpacePosition.y - sunsqH / 2, sunsqW, sunsqH)
        p.postprocessing.godraysFakeSunUniforms.fAspect.value = window.innerWidth / window.innerHeight
        p.postprocessing.scene.overrideMaterial = p.postprocessing.materialGodraysFakeSun
        p.renderer.render(p.postprocessing.scene, p.postprocessing.camera, p.postprocessing.rtTextureColors)
        p.renderer.setScissorTest(False)

        # Colors

        p.scene.overrideMaterial = None
        p.renderer.render(p.scene, p.camera, p.postprocessing.rtTextureColors)

        # Depth

        p.scene.overrideMaterial = p.materialDepth
        p.renderer.render(p.scene, p.camera, p.postprocessing.rtTextureDepth, True)

        # -- Render god-rays --

        # Maximum length of god-rays (in texture space [0,1]X[0,1])

        filterLen = 1.0

        # Samples taken by filter

        TAPS_PER_PASS = 6.0

        # Pass order could equivalently be 3,2,1 (instead of 1,2,3), which
        # would start with a small filter support and grow to large. however
        # the large-to-small order produces less objectionable aliasing artifacts that
        # appear as a glimmer along the length of the beams

        # pass 1 - render into first ping-pong target

        pass1 = 1.0
        stepLen = filterLen * math.pow(TAPS_PER_PASS, -pass1)

        p.postprocessing.godrayGenUniforms.fStepSize.value = stepLen
        p.postprocessing.godrayGenUniforms.tInput.value = p.postprocessing.rtTextureDepth.texture

        p.postprocessing.scene.overrideMaterial = p.postprocessing.materialGodraysGenerate
        p.renderer.clearTarget(p.postprocessing.rtTextureGodRays2, True, True, False)

        p.renderer.render(p.postprocessing.scene, p.postprocessing.camera, p.postprocessing.rtTextureGodRays2)

        # pass 2 - render into second ping-pong target

        pass1 = 2.0
        stepLen = filterLen * math.pow(TAPS_PER_PASS, -pass1)

        p.postprocessing.godrayGenUniforms.fStepSize.value = stepLen
        p.postprocessing.godrayGenUniforms.tInput.value = p.postprocessing.rtTextureGodRays2.texture

        p.renderer.clearTarget(p.postprocessing.rtTextureGodRays1, True, True, False)
        p.renderer.render(p.postprocessing.scene, p.postprocessing.camera, p.postprocessing.rtTextureGodRays1 )

        # pass 3 - 1st RT

        pass1 = 3.0
        stepLen = filterLen * math.pow(TAPS_PER_PASS, -pass1)

        p.postprocessing.godrayGenUniforms.fStepSize.value = stepLen
        p.postprocessing.godrayGenUniforms.tInput.value = p.postprocessing.rtTextureGodRays1.texture

        p.renderer.render(p.postprocessing.scene, p.postprocessing.camera , p.postprocessing.rtTextureGodRays2 )

        # final pass - composite god-rays onto colors

        p.postprocessing.godrayCombineUniforms.tColors.value = p.postprocessing.rtTextureColors.texture
        p.postprocessing.godrayCombineUniforms.tGodRays.value = p.postprocessing.rtTextureGodRays2.texture

        p.postprocessing.scene.overrideMaterial = p.postprocessing.materialGodraysCombine

        p.renderer.render(p.postprocessing.scene, p.postprocessing.camera)
        p.postprocessing.scene.overrideMaterial = None

    else:
        p.renderer.clear()

        p.renderer.render(p.scene, p.camera)


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
