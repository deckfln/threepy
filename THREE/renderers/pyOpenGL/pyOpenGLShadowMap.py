"""
/**
 * @author alteredq / http:# //alteredqualia.com/
 * @author mrdoob / http:# //mrdoob.com/
 */
"""

from THREE.Frustum import *
from THREE.materials.MeshDepthMaterial import *
from THREE.materials.MeshDistanceMaterial import *
from THREE.renderers.pyOpenGLRenderTarget import *


class pyOpenGLShadowMap(pyOpenGLObject):
    def __init__(self, _renderer, _objects, maxTextureSize ):
        self._renderer = _renderer
        self._objects = _objects
        self._frustum = Frustum()

        self._projScreenMatrix = Matrix4()

        self._shadowMapSize = Vector2()
        self._maxShadowMapSize = Vector2( maxTextureSize, maxTextureSize )

        self._lookTarget = Vector3()
        self._lightPositionWorld = Vector3()

        self._MorphingFlag = 1
        self._SkinningFlag = 2

        _NumberOfMaterialVariants = ( self._MorphingFlag | self._SkinningFlag ) + 1

        self._depthMaterials = [ None for i in range(_NumberOfMaterialVariants)]
        self._distanceMaterials = [ None for i in range(_NumberOfMaterialVariants )]

        self._materialCache = {}

        self.shadowSide = {0: BackSide, 1: FrontSide, 2: DoubleSide}

        self.cubeDirections = [
            Vector3( 1, 0, 0 ), Vector3( - 1, 0, 0 ), Vector3( 0, 0, 1 ),
            Vector3( 0, 0, - 1 ), Vector3( 0, 1, 0 ), Vector3( 0, - 1, 0 )
        ]

        self.cubeUps = [
            Vector3( 0, 1, 0 ), Vector3( 0, 1, 0 ), Vector3( 0, 1, 0 ),
            Vector3( 0, 1, 0 ), Vector3( 0, 0, 1 ),    Vector3( 0, 0, - 1 )
        ]

        self.cube2DViewPorts = [
            Vector4(), Vector4(), Vector4(),
            Vector4(), Vector4(), Vector4()
        ]

        # // init

        for i in range(_NumberOfMaterialVariants):
            useMorphing = ( i & self._MorphingFlag ) != 0
            useSkinning = ( i & self._SkinningFlag ) != 0

            depthMaterial = MeshDepthMaterial( {
                'depthPacking': RGBADepthPacking,
                'morphTargets': useMorphing,
                'skinning': useSkinning

            } )

            self._depthMaterials[ i ] = depthMaterial

            # //

            distanceMaterial = MeshDistanceMaterial( {
                'morphTargets': useMorphing,
                'skinning': useSkinning

            } )

            self._distanceMaterials[ i ] = distanceMaterial

        # //

        self.enabled = False

        self.autoUpdate = True
        self.needsUpdate = False

        self.type = PCFShadowMap

    def render(self, lights, scene, camera ):
        if not self.enabled:
            return
        if not self.autoUpdate and not self.needsUpdate:
            return

        if len(lights) == 0:
            return

        # // TODO Clean up (needed in case of contextlost)
        _state = self._renderer.state

        # // Set GL state for depth map.
        _state.disable( GL_BLEND )
        _state.buffers.color.setClear( 1, 1, 1, 1 )
        _state.buffers.depth.setTest( True )
        _state.setScissorTest( False )

        # // render depth map

        for light in lights:
            shadow = light.shadow
            is_PointLight = light and light.my_class(isPointLight)

            if shadow is None:
                print( 'THREE.WebGLShadowMap:', light, 'has no shadow.' )
                continue

            shadowCamera = shadow.camera

            self._shadowMapSize.copy( shadow.mapSize )
            self._shadowMapSize.min( self._maxShadowMapSize )

            if is_PointLight:
                vpWidth = self._shadowMapSize.x
                vpHeight = self._shadowMapSize.y

                # // These viewports map a cube-map onto a 2D texture with the
                # // following orientation:
                # //
                # //  xzXZ
                # //   y Y
                # //
                # // X - Positive x direction
                # // x - Negative x direction
                # // Y - Positive y direction
                # // y - Negative y direction
                # // Z - Positive z direction
                # // z - Negative z direction

                # // positive X
                self.cube2DViewPorts[ 0 ].set( vpWidth * 2, vpHeight, vpWidth, vpHeight )
                # // negative X
                self.cube2DViewPorts[ 1 ].set( 0, vpHeight, vpWidth, vpHeight )
                # // positive Z
                self.cube2DViewPorts[ 2 ].set( vpWidth * 3, vpHeight, vpWidth, vpHeight )
                # // negative Z
                self.cube2DViewPorts[ 3 ].set( vpWidth, vpHeight, vpWidth, vpHeight )
                # // positive Y
                self.cube2DViewPorts[ 4 ].set( vpWidth * 3, 0, vpWidth, vpHeight )
                # // negative Y
                self.cube2DViewPorts[ 5 ].set( vpWidth, 0, vpWidth, vpHeight )

                self._shadowMapSize.x *= 4.0
                self._shadowMapSize.y *= 2.0

            if shadow.map is None:
                pars = { 'minFilter': NearestFilter, 'magFilter': NearestFilter, 'format': RGBAFormat }

                shadow.map = pyOpenGLRenderTarget( self._shadowMapSize.x, self._shadowMapSize.y, pars )
                shadow.map.texture.name = light.name + ".shadowMap"

                shadowCamera.updateProjectionMatrix()

            if shadow.my_class(isSpotLightShadow):
                shadow.update( light )

            shadowMap = shadow.map
            shadowMatrix = shadow.matrix

            self._lightPositionWorld.setFromMatrixPosition( light.matrixWorld )
            shadowCamera.position.copy( self._lightPositionWorld )

            if is_PointLight:
                faceCount = 6

                # // for point lights we set the shadow matrix to be a translation-only matrix
                # // equal to inverse of the light's position

                shadowMatrix.makeTranslation( - self._lightPositionWorld.x, - self._lightPositionWorld.y, - self._lightPositionWorld.z )

            else:
                faceCount = 1

                self._lookTarget.setFromMatrixPosition( light.target.matrixWorld )
                shadowCamera.lookAt( self._lookTarget )
                shadowCamera.updateMatrixWorld()

                # // compute shadow matrix

                shadowMatrix.set(
                    0.5, 0.0, 0.0, 0.5,
                    0.0, 0.5, 0.0, 0.5,
                    0.0, 0.0, 0.5, 0.5,
                    0.0, 0.0, 0.0, 1.0
                )

                shadowMatrix.multiply( shadowCamera.projectionMatrix )
                shadowMatrix.multiply( shadowCamera.matrixWorldInverse )

            self._renderer.setRenderTarget( shadowMap )
            self._renderer.clear()

            # // render shadow map for each cube face (if omni-directional) or
            # // run a single pass if not

            for face in range(faceCount):
                if is_PointLight:
                    self._lookTarget.copy( shadowCamera.position )
                    self._lookTarget.add( self.cubeDirections[ face ] )
                    shadowCamera.up.copy( self.cubeUps[ face ] )
                    shadowCamera.lookAt( self._lookTarget )
                    shadowCamera.updateMatrixWorld()

                    vpDimensions = self.cube2DViewPorts[ face ]
                    _state.viewport( vpDimensions )

                # // update camera matrices and frustum

                self._projScreenMatrix.multiplyMatrices( shadowCamera.projectionMatrix, shadowCamera.matrixWorldInverse )
                self._frustum.setFromMatrix( self._projScreenMatrix )

                # // set object matrices & frustum culling

                self.renderObject( scene, camera, shadowCamera, is_PointLight )

        self.needsUpdate = False

    def getDepthMaterial(self, object, material, is_PointLight, lightPositionWorld, shadowCameraNear, shadowCameraFar ):
        geometry = object.geometry

        result = None

        materialVariants = self._depthMaterials
        customMaterial = object.customDepthMaterial

        if is_PointLight:
            materialVariants = self._distanceMaterials
            customMaterial = object.customDistanceMaterial

        if not customMaterial:
            useMorphing = False

            if material.morphTargets:
                if geometry and geometry.my_class(isBufferGeometry):
                    useMorphing = geometry.morphAttributes and geometry.morphAttributes.position and geometry.morphAttributes.position.length > 0

                elif geometry and geometry.my_class(isGeometry):
                    useMorphing = geometry.morphTargets and geometry.morphTargets.length > 0

            if object.is_a('SkinnedMesh') and material.skinning == False:
                print( 'THREE.WebGLShadowMap: THREE.SkinnedMesh with material.skinning set to False:', object )

            useSkinning = object.is_a('SkinnedMesh') and material.skinning

            variantIndex = 0

            if useMorphing:
                variantIndex |= self._MorphingFlag
            if useSkinning:
                variantIndex |= self._SkinningFlag

            result = materialVariants[ variantIndex ]

        else:
            result = customMaterial

        if self._renderer.localClippingEnabled and \
                material.clipShadows and \
                len(material.clippingPlanes) != 0:

            # // in self case we need a unique material instance reflecting the
            # // appropriate state

            keyA = result.uuid
            keyB = material.uuid

            if keyA not in self._materialCache:
                materialsForVariant = {}
                self._materialCache[keyA] = materialsForVariant
            else:
                materialsForVariant = self._materialCache[ keyA ]


            if keyB not in materialsForVariant:
                cachedMaterial = result.clone()
                materialsForVariant[keyB] = cachedMaterial
            else:
                cachedMaterial = materialsForVariant[ keyB ]

            result = cachedMaterial

        result.visible = material.visible
        result.wireframe = material.wireframe

        result.side = material.shadowSide if material.shadowSide is not None else self.shadowSide[material.side]

        result.clipShadows = material.clipShadows
        result.clippingPlanes = material.clippingPlanes
        result.clipIntersection = material.clipIntersection

        result.wireframeLinewidth = material.wireframeLinewidth
        result.linewidth = material.linewidth if hasattr(material, 'linewidth') else None

        if is_PointLight and result.my_class(isMeshDistanceMaterial):
            result.referencePosition.copy( lightPositionWorld )
            result.nearDistance = shadowCameraNear
            result.farDistance = shadowCameraFar

        return result

    def renderObject(self, object, camera, shadowCamera, is_PointLight ):
        if not object.visible:
            return

        visible = object.layers.test( camera.layers )

        if visible and ( object.my_class(isMesh) or object.my_class(isLine) or object.my_class(isPoints) ):
            if object.castShadow and ( not object.frustumCulled or self._frustum.intersectsObject( object ) ):
                object.modelViewMatrix.multiplyMatrices( shadowCamera.matrixWorldInverse, object.matrixWorld )

                geometry = self._objects.update( object )
                material = object.material

                if isinstance(material, list ):
                    groups = geometry.groups

                    for group in groups:
                        groupMaterial = material[ group.materialIndex ]

                        if groupMaterial and groupMaterial.visible:
                            depthMaterial = self.getDepthMaterial( object, groupMaterial, is_PointLight, self._lightPositionWorld, shadowCamera.near, shadowCamera.far )
                            self._renderer.renderBufferDirect( shadowCamera, None, geometry, depthMaterial, object, group, isShadowMapRenderer)

                elif material.visible:
                    depthMaterial = self.getDepthMaterial( object, material, is_PointLight, self._lightPositionWorld, shadowCamera.near, shadowCamera.far )
                    self._renderer.renderBufferDirect( shadowCamera, None, geometry, depthMaterial, object, None, isShadowMapRenderer)

        for child in object.children:
            self.renderObject( child, camera, shadowCamera, is_PointLight )
