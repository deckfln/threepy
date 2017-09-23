"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.Color import *
from THREE.Camera import *
from THREE.BoxBufferGeometry import *
from THREE.PlaneBufferGeometry import *
from THREE.ShaderMaterial import *
from THREE.ShaderLib import *
from THREE.Mesh import *


def _onBeforeRenderBackgroup(self, renderer, scene, camera ):
    scale = camera.far

    self.matrixWorld.makeScale( scale, scale, scale )
    self.matrixWorld.copyPosition( camera.matrixWorld )

    self.material.polygonOffsetUnits = scale * 10

    
class pyOpenGLBackground:
    def __init__(self, renderer, state, geometries, premultipliedAlpha ):
        self.clearColor = Color( 0x000000 )
        self.clearAlpha = 0

        self.planeCamera = None
        self.planeMesh = None
        self.boxMesh = None

        self.renderer = renderer
        self.state = state
        self.geometries = geometries
        self.premultipliedAlpha = premultipliedAlpha
        
    def render( self, renderList, scene, camera, forceClear ):
        background = scene.background

        if background is None:
            self.setClear( self.clearColor, self.clearAlpha )
        elif background and background.isColor:
            self.setClear( background, 1 )
            forceClear = True

        if self.renderer.autoClear or forceClear:
            self.renderer.clear( self.renderer.autoClearColor, self.renderer.autoClearDepth, self.renderer.autoClearStencil )

        if background and background.isCubeTexture:
            if self.boxMesh is None:
                self.boxMesh = Mesh(
                    BoxBufferGeometry( 1, 1, 1 ),
                    ShaderMaterial( {
                        'uniforms': ShaderLib.cube.uniforms,
                        'vertexShader': ShaderLib.cube.vertexShader,
                        'fragmentShader': ShaderLib.cube.fragmentShader,
                        'side': BackSide,
                        'depthTest': True,
                        'depthWrite': False,
                        'polygonOffset': True,
                        'fog': False
                    } )
                )

                self.boxMesh.geometry.removeAttribute( 'normal' )
                self.boxMesh.geometry.removeAttribute( 'uv' )

                self.boxMesh.setOnBeforeRender(self, _onBeforeRenderBackgroup)

                self.geometries.update( self.boxMesh.geometry )

            self.boxMesh.material.uniforms.tCube.value = background

            renderList.push( self.boxMesh, self.boxMesh.geometry, self.boxMesh.material, 0, None )

        elif background and background.isTexture:
            if self.planeCamera is None:
                planeCamera = OrthographicCamera( - 1, 1, 1, - 1, 0, 1 )

                planeMesh = Mesh(
                    PlaneBufferGeometry( 2, 2 ),
                    MeshBasicMaterial( { 'depthTest': False, 'depthWrite': False, 'fog': False } )
                )

                self.geometries.update( planeMesh.geometry )

            planeMesh.material.map = self.background

            # // TODO Push this to renderList

            self.renderer.renderBufferDirect( self.planeCamera, None, planeMesh.geometry, planeMesh.material, planeMesh, None )

    def setClear(self, color, alpha ):
        self.state.buffers.color.setClear( color.r, color.g, color.b, alpha, self.premultipliedAlpha )

    def getClearColor(self):
        return self.clearColor

    def setClearColor(self, color, alpha ):
        self.clearColor.set( color )
        self.clearAlpha = alpha if alpha else 1
        self.setClear( self.clearColor, self.clearAlpha )

    def getClearAlpha(self):
        return self.clearAlpha

    def setClearAlpha(self, alpha ):
        self.clearAlpha = alpha
        self.setClear( self.clearColor, self.clearAlpha )
