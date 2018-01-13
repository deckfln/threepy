"""
        <title>three.js webgl-camera cinematic</title>
"""
import sys
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.Constants import *
import THREE._Math as _Math
from THREE.cameras.CinematicCamera import *
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.container = None
        self.camera = None
        self.scene = None
        self.raycaster = None
        self.renderer = None
        self.mouse = THREE.Vector2()
        self.INTERSECTED = None
        self.radius = 100
        self.theta = 0


def init(p):
    p.container = pyOpenGL(p)

    p.camera = CinematicCamera( 60, p.container.clientWidth / p.container.clientHeight, 1, 1000 )
    p.camera.setLens(5)
    p.camera.position.set(2, 1, 500)

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0xf0f0f0 )

    p.scene.add( THREE.AmbientLight( 0xffffff, 0.3 ) )

    light = THREE.DirectionalLight( 0xffffff, 0.35 )
    light.position.set( 1, 1, 1 ).normalize()
    p.scene.add( light )

    geometry = THREE.BoxGeometry( 20, 20, 20 )

    for i in range(1500):
        object = THREE.Mesh( geometry, THREE.MeshLambertMaterial( { 'color': random.random() * 0xffffff } ) )

        object.position.x = random.random() * 800 - 400
        object.position.y = random.random() * 800 - 400
        object.position.z = random.random() * 800 - 400

        p.scene.add( object )

    p.raycaster = THREE.Raycaster()

    p.renderer = THREE.pyOpenGLRenderer( { 'antialias': True } )
    p.renderer.setSize( p.container.clientWidth, p.container.clientHeight )

    p.container.addEventListener( 'mousemove', onDocumentMouseMove, False )
    p.container.addEventListener( 'resize', onWindowResize, False )

    effectController  = {
        'focalLength': 15,
        # // jsDepthCalculation: true,
        # // shaderFocus: false,
        # //
        'fstop': 2.8,
        # // maxblur: 1.0,
        # //
        'showFocus': False,
        'focalDepth': 3,
        # // manualdof: false,
        # // vignetting: false,
        # // depthblur: false,
        # //
        # // threshold: 0.5,
        # // gain: 2.0,
        # // bias: 0.5,
        # // fringe: 0.7,
        # //
        # // focalLength: 35,
        # // noise: true,
        # // pentagon: false,
        # //
        # // dithering: 0.0001
    }

    def matChanger():
        for e in effectController:
            if e in p.camera.postprocessing.bokeh_uniforms:
                p.camera.postprocessing.bokeh_uniforms[ e ].value = effectController[ e ]

        p.camera.postprocessing.bokeh_uniforms[ 'znear' ].value = p.camera.near
        p.camera.postprocessing.bokeh_uniforms[ 'zfar' ].value = p.camera.far
        p.camera.setLens(effectController['focalLength'], p.camera.frameHeight ,effectController['fstop'], p.camera.coc)
        effectController['focalDepth'] = p.camera.postprocessing.bokeh_uniforms["focalDepth"].value

    matChanger()

    p.container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event, p):
    height = event.height
    width = event.width
    p.camera.aspect = width / height
    p.camera.updateProjectionMatrix()

    p.renderer.setSize(width, height)


def onDocumentMouseMove( event, p ):
    event.preventDefault()

    p.mouse.x = ( event.clientX / p.container.clientWidth ) * 2 - 1
    p.mouse.y = - ( event.clientY / p.container.clientHeight ) * 2 + 1


def animate(p):
    render(p)


def render(p):
    p.theta += 0.1

    p.camera.position.x = p.radius * math.sin( _Math.degToRad( p.theta ) )
    p.camera.position.y = p.radius * math.sin( _Math.degToRad( p.theta ) )
    p.camera.position.z = p.radius * math.cos( _Math.degToRad( p.theta ) )
    p.camera.lookAt( p.scene.position )

    p.camera.updateMatrixWorld()

    # // find intersections

    p.raycaster.setFromCamera( p.mouse, p.camera )

    intersects = p.raycaster.intersectObjects( p.scene.children )

    if len(intersects) > 0:
        targetDistance = intersects[ 0 ].distance
        
        # // Using Cinematic camera focusAt method
        p.camera.focusAt(targetDistance)

        if p.INTERSECTED != intersects[ 0 ].object:
            if p.INTERSECTED:
                p.INTERSECTED.material.emissive.setHex( p.INTERSECTED.currentHex )

            p.INTERSECTED = intersects[ 0 ].object
            p.INTERSECTED.currentHex = p.INTERSECTED.material.emissive.getHex()
            p.INTERSECTED.material.emissive.setHex( 0xff0000 )
    else:
        if p.INTERSECTED:
            p.INTERSECTED.material.emissive.setHex( p.INTERSECTED.currentHex )

        p.INTERSECTED = None

    if p.camera.postprocessing.enabled:
        # //rendering Cinematic Camera effects
        p.camera.renderCinematic(p.scene, p.renderer)
    else:
        p.scene.overrideMaterial = None

        p.renderer.clear()
        p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
