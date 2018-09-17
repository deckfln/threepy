"""
    <title>three.js webgl - buffergeometry - lines</title>
"""        
import random
from datetime import datetime
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.mesh = None


def init(p):
    p.container = pyOpenGL(p)

    p.camera = THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 1, 3500)
    p.camera.position.z = 2750

    p.scene = THREE.Scene()

    segments = 10000

    geometry = THREE.BufferGeometry()
    material = THREE.LineBasicMaterial({ 'vertexColors': THREE.VertexColors })

    positions = Float32Array( segments * 3 )
    colors = Float32Array( segments * 3 )

    r = 800

    for i in range(segments):
        x = random.random() * r - r / 2
        y = random.random() * r - r / 2
        z = random.random() * r - r / 2

        # // positions

        positions[ i * 3 ] = x
        positions[ i * 3 + 1 ] = y
        positions[ i * 3 + 2 ] = z

        # // colors

        colors[ i * 3 ] = ( x / r ) + 0.5
        colors[ i * 3 + 1 ] = ( y / r ) + 0.5
        colors[ i * 3 + 2 ] = ( z / r ) + 0.5

    geometry.addAttribute( 'position', THREE.BufferAttribute( positions, 3 ) )
    geometry.addAttribute( 'color', THREE.BufferAttribute( colors, 3 ) )

    geometry.computeBoundingSphere()

    p.mesh = THREE.Line( geometry, material )
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
    time = datetime.now().timestamp()

    p.mesh.rotation.x = time * 0.25
    p.mesh.rotation.y = time * 0.5

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
