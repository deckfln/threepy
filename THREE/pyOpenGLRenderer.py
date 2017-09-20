"""
/**
 * @author supereggbert / http://www.paulbrunt.co.uk/
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 * @author szimek / https://github.com/szimek/
 * @author tschw
 */
"""
from THREE.pyOpenGL import *


class pyOpenGLRenderer:
	def __init__(self, parameters=None ):
	
	def initGLContext(self):
		extensions = pyOpenGLExtensions( )
		extensions.get( 'WEBGL_depth_texture' )
		extensions.get( 'OES_texture_float' )
		extensions.get( 'OES_texture_float_linear' )
		extensions.get( 'OES_texture_half_float' )
		extensions.get( 'OES_texture_half_float_linear' )
		extensions.get( 'OES_standard_derivatives' )
		extensions.get( 'ANGLE_instanced_arrays' )

		if extensions.get( 'OES_element_index_uint' ):
			BufferGeometry.MaxIndex = 4294967296

		utils = new pyOpenGLUtils( extensions )

		capabilities = pyOpenGLCapabilities( extensions, parameters )

		state = pyOpenGLState( extensions, utils )
		state.scissor( _currentScissor.copy( _scissor ).multiplyScalar( _pixelRatio ) )
		state.viewport( _currentViewport.copy( _viewport ).multiplyScalar( _pixelRatio ) )

		properties = pyOpenGLProperties()
		textures = pyOpenGLTextures( _gl, extensions, state, properties, capabilities, utils, _infoMemory )
		attributes = pyOPenGLAttributes( _gl )
		geometries = new WebGLGeometries( _gl, attributes, _infoMemory )
		objects = new WebGLObjects( geometries, _infoRender )
		morphtargets = new WebGLMorphtargets( _gl )
		programCache = new WebGLPrograms( _this, extensions, capabilities )
		lights = new WebGLLights()
		renderLists = new WebGLRenderLists()

		background = new WebGLBackground( _this, state, geometries, _premultipliedAlpha )

		bufferRenderer = new WebGLBufferRenderer( _gl, extensions, _infoRender )
		indexedBufferRenderer = new WebGLIndexedBufferRenderer( _gl, extensions, _infoRender )

		flareRenderer = new WebGLFlareRenderer( _this, _gl, state, textures, capabilities )
		spriteRenderer = new WebGLSpriteRenderer( _this, _gl, state, textures, capabilities )

		_this.info.programs = programCache.programs

		_this.context = _gl
		_this.capabilities = capabilities
		_this.extensions = extensions
		_this.properties = properties
		_this.renderLists = renderLists
		_this.state = state

	}