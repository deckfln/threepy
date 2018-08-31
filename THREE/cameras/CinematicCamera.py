"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author greggman / http:# //games.greggman.com/
 * @author zz85 / http:# //www.lab4games.net/zz85/blog
 * @author kaypiKun
 */
"""
from THREE.cameras.Camera import *
from THREE.shaders.BokehShader2 import *
import THREE.pyOpenGL.pyOpenGL
import THREE.pyOpenGL.window as window


class _PostProcessing:
    def __init__(self, enabled):
        self.enabled = enabled
        self.scene = None
        self.camera = None
        self.rtTextureDepth = None
        self.rtTextureColor = None
        self.bokeh_uniforms = None
        self.materialBokeh = None
        self.quad = None


class CinematicCamera(PerspectiveCamera):
    def __init__(self, fov, aspect, near, far ):
        super().__init__( fov, aspect, near, far )

        self.type = "CinematicCamera"

        self.postprocessing = _PostProcessing(True)
        self.shaderSettings = {
            'rings': 3,
            'samples': 4
        }

        self.material_depth = THREE.MeshDepthMaterial()
        self.frameHeight = None

        # // In case of cinematicCamera, having a default lens set is important
        self.setLens()

        self.initPostProcessing()

    def setLens(self, focalLength=35, filmGauge=None, fNumber=8, coc=0.019 ):
        """
        # // providing fnumber and coc(Circle of Confusion) as extra arguments
        """
        # // In case of cinematicCamera, having a default lens set is important
        if filmGauge is not None:
            self.filmGauge = filmGauge

        self.setFocalLength( focalLength )

        # // if fnumber and coc are not provided, cinematicCamera tries to act as a basic PerspectiveCamera
        self.fNumber = fNumber
        self.coc = coc

        # // fNumber is focalLength by aperture
        self.aperture = focalLength / self.fNumber

        # // hyperFocal is required to calculate depthOfField when a lens tries to focus at a distance with given fNumber and focalLength
        self.hyperFocal = ( focalLength * focalLength ) / ( self.aperture * self.coc )

    def linearize(self, depth ):
        zfar = self.far
        znear = self.near
        return - zfar * znear / ( depth * ( zfar - znear ) - zfar )

    def smoothstep(self, near, far, depth ):
        x = self.saturate( ( depth - near ) / ( far - near ) )
        return x * x * ( 3 - 2 * x )

    def saturate(self, x ):
        return max( 0, min( 1, x ) )

    def focusAt(self, focusDistance=20 ):
        """
        # // function for focusing at a distance from the camera
        """

        focalLength = self.getFocalLength()

        # // distance from the camera (normal to frustrum) to focus on
        self.focus = focusDistance

        # // the nearest point from the camera which is in focus (unused)
        self.nearPoint = ( self.hyperFocal * self.focus ) / ( self.hyperFocal + ( self.focus - focalLength ) )

        # // the farthest point from the camera which is in focus (unused)
        self.farPoint = ( self.hyperFocal * self.focus ) / ( self.hyperFocal - ( self.focus - focalLength ) )

        # // the gap or width of the space in which is everything is in focus (unused)
        self.depthOfField = self.farPoint - self.nearPoint

        # // Considering minimum distance of focus for a standard lens (unused)
        if self.depthOfField < 0:
            self.depthOfField = 0

        self.sdistance = self.smoothstep( self.near, self.far, self.focus )

        self.ldistance = self.linearize( 1 -    self.sdistance )

        self.postprocessing.bokeh_uniforms[ 'focalDepth' ].value = self.ldistance

    def initPostProcessing(self):
        if self.postprocessing.enabled:

            self.postprocessing.scene = THREE.Scene()

            self.postprocessing.camera = THREE.OrthographicCamera( window.innerWidth / - 2, window.innerWidth / 2,    window.innerHeight / 2, window.innerHeight / - 2, - 10000, 10000 )

            self.postprocessing.scene.add( self.postprocessing.camera )

            pars = { 'minFilter': THREE.LinearFilter, 'magFilter': THREE.LinearFilter, 'format': THREE.RGBFormat }
            self.postprocessing.rtTextureDepth = THREE.pyOpenGLRenderTarget( window.innerWidth, window.innerHeight, pars )
            self.postprocessing.rtTextureColor = THREE.pyOpenGLRenderTarget( window.innerWidth, window.innerHeight, pars )

            bokeh_shader = BokehShader

            self.postprocessing.bokeh_uniforms = THREE.UniformsUtils.clone( bokeh_shader.uniforms )

            self.postprocessing.bokeh_uniforms[ "tColor" ].value = self.postprocessing.rtTextureColor.texture
            self.postprocessing.bokeh_uniforms[ "tDepth" ].value = self.postprocessing.rtTextureDepth.texture

            self.postprocessing.bokeh_uniforms[ "manualdof" ].value = 0
            self.postprocessing.bokeh_uniforms[ "shaderFocus" ].value = 0

            self.postprocessing.bokeh_uniforms[ "fstop" ].value = 2.8

            self.postprocessing.bokeh_uniforms[ "showFocus" ].value = 1

            self.postprocessing.bokeh_uniforms[ "focalDepth" ].value = 0.1

            # //console.log( self.postprocessing.bokeh_uniforms[ "focalDepth" ].value )

            self.postprocessing.bokeh_uniforms[ "znear" ].value = self.near
            self.postprocessing.bokeh_uniforms[ "zfar" ].value = self.near


            self.postprocessing.bokeh_uniforms[ "textureWidth" ].value = window.innerWidth

            self.postprocessing.bokeh_uniforms[ "textureHeight" ].value = window.innerHeight

            self.postprocessing.materialBokeh = THREE.ShaderMaterial( {
                'uniforms': self.postprocessing.bokeh_uniforms,
                'vertexShader': bokeh_shader.vertexShader,
                'fragmentShader': bokeh_shader.fragmentShader,
                'defines': {
                    'RINGS': self.shaderSettings['rings'],
                    'SAMPLES': self.shaderSettings['samples']
                }
            } )

            self.postprocessing.quad = THREE.Mesh( THREE.PlaneBufferGeometry( window.innerWidth, window.innerHeight ), self.postprocessing.materialBokeh )
            self.postprocessing.quad.position.z = - 500
            self.postprocessing.scene.add( self.postprocessing.quad )

    def renderCinematic(self, scene, renderer ):
        if self.postprocessing.enabled:
            renderer.clear()

            # // Render scene into texture

            scene.overrideMaterial = None
            renderer.render( scene, self, self.postprocessing.rtTextureColor, True )

            # // Render depth into texture

            scene.overrideMaterial = self.material_depth
            renderer.render( scene, self, self.postprocessing.rtTextureDepth, True )

            # // Render bokeh composite

            renderer.render( self.postprocessing.scene, self.postprocessing.camera )
