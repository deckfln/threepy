"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.cameras.Camera import *
from THREE.geometries.BoxBufferGeometry import *
from THREE.geometries.PlaneGeometry import *
from THREE.renderers.shaders.ShaderLib import *
from THREE.objects.Mesh import *


class pyOpenGLBackground:
    def __init__(self, renderer, state, objects, premultipliedAlpha ):
        self.clearColor = Color( 0x000000 )
        self.clearAlpha = 0

        self.planeCamera = None
        self.planeMesh = None
        self.boxMesh = None
        self.boxMesh_vertex = ShaderLib['cube'].getVertexShader()
        self.boxMesh_fragment = ShaderLib['cube'].getFragmentShader()
        self.boxMesh_uniforms = ShaderLib['cube'].uniforms

        self.renderer = renderer
        self.state = state
        self.objects = objects
        self.premultipliedAlpha = premultipliedAlpha

    def render( self, renderList, scene, camera, forceClear ):
        background = scene.background

        if background is None:
            self.setClear( self.clearColor, self.clearAlpha )
        elif background and background.my_class(isColor):
            self.setClear( background, 1 )
            forceClear = True

        if self.renderer.autoClear or forceClear:
            self.renderer.clear( self.renderer.autoClearColor, self.renderer.autoClearDepth, self.renderer.autoClearStencil )

        if background and background.my_class(isCubeTexture):
            if self.boxMesh is None:
                self.boxMesh = Mesh(
                    BoxBufferGeometry( 1, 1, 1 ),
                    ShaderMaterial( {
                        'uniforms': self.boxMesh_uniforms,
                        'vertexShader': self.boxMesh_vertex,
                        'fragmentShader': self.boxMesh_fragment,
                        'side': BackSide,
                        'depthTest': True,
                        'depthWrite': False,
                        'fog': False
                    } )
                )

                self.boxMesh.geometry.removeAttribute( 'normal' )
                self.boxMesh.geometry.removeAttribute( 'uv' )

                def _onBeforeRenderBackgroup(object, renderer, scene, camera, geometry=None, material=None, group=None):
                    scale = camera.far

                    object.matrixWorld.makeScale(scale, scale, scale)
                    object.matrixWorld.copyPosition(camera.matrixWorld)

                    object.matrixWorld.is_updated()

                    #object.material.polygonOffsetUnits = scale * 10

                self.boxMesh.setOnBeforeRender(self, _onBeforeRenderBackgroup)

                self.objects.update( self.boxMesh)

            self.boxMesh.material.uniforms.tCube.value = background

            renderList.push( self.boxMesh, self.boxMesh.geometry, self.boxMesh.material, 0, None )

        elif background and background.my_class(isTexture):
            if self.planeCamera is None:
                self.planeCamera = OrthographicCamera( - 1, 1, 1, - 1, 0, 1 )

                self.planeMesh = Mesh(
                    PlaneBufferGeometry( 2, 2 ),
                    MeshBasicMaterial( { 'depthTest': False, 'depthWrite': False, 'fog': False } )
                )

                self.objects.update( self.planeMesh )

            self.planeMesh.material.map = background

            # // TODO Push this to renderList

            glBindVertexArray(self.boxMesh.vao)
            self.renderer.renderBufferDirect( self.planeCamera, None, self.planeMesh.geometry, self.planeMesh.material, planeMesh, None, isViewRenderer)
            glBindVertexArray(0)

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
