"""
        <title>three.js webgl - glTF loader</title>
        <div id="info">
            <a href="http://threejs.org" target="_blank" rel="noopener">three.js</a> - GLTFLoader<br />
            Battle Damaged Sci-fi Helmet by
            <a href="https://sketchfab.com/theblueturtle_" target="_blank" rel="noopener">theblueturtle_</a><br />
        </div>
"""
import sys, os.path
mango_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) )
sys.path.append(mango_dir)


from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.OrbitControls import *
from THREE.loaders.GLTFLoader import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.elf = None
        self.clock = None
        self.container = None
        self.stats = None
        self.controls = None
        self.light = None


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)
    p.renderer.gammaOutput = True

    p.camera = THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 0.25, 20 )
    p.camera.position.set( -1.8, 0.9, 2.7 )

    p.controls = OrbitControls(p.camera, p.container)
    p.controls.target.set( 0, -0.2, -0.2 )
    p.controls.update()

    # envmap
    path = 'textures/cube/Bridge2/'
    format = '.jpg'
    envMap = THREE.CubeTextureLoader().load( [
        path + 'posx' + format, path + 'negx' + format,
        path + 'posy' + format, path + 'negy' + format,
        path + 'posz' + format, path + 'negz' + format
    ])

    p.scene = THREE.Scene()
    p.scene.background = envMap

    p.light = THREE.HemisphereLight( 0xbbbbff, 0x444422 )
    #p.light = THREE.AmbientLight( 0xffffff)
    p.light.position.set( 0, 1, 0 )
    p.scene.add( p.light )

    # model
    def function(gltf):
        def fn(child, scope):
            if child.my_class(isMesh):
                child.material.envMap = envMap

        gltf.scene.traverse(fn)
        p.scene.add(gltf.scene)

    loader = GLTFLoader()
    loader.load( 'models/gltf/DamagedHelmet/glTF/DamagedHelmet.gltf', function)


def onWindowResize(event, p):
    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(p):
    render(p)


def render(p):
    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
