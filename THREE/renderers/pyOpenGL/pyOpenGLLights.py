"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.math.Vector2 import *
from THREE.math.Vector3 import *
from THREE.math.Matrix4 import *
from THREE.math.Color import *


class _LightUniforms:
    def __init__(self):
        self.type="_LightUniforms"

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, item):
        return self.__dict__[item]


class _DirectionalLightUniforms(_LightUniforms):
    def __init__(self):
        super().__init__()
        self.direction = Vector3()
        self.color = Color()
        self.shadow = False
        self.shadowBias = 0.0
        self.shadowRadius = 1.0
        self.shadowMapSize = Vector2()


class _SpotLightUniforms(_LightUniforms):
    def __init__(self):
        super().__init__()
        self.position = Vector3()
        self.direction = Vector3()
        self.color = Color()
        self.distance = 0
        self.coneCos = 0
        self.penumbraCos = 0
        self.decay = 0
        self.shadow = False
        self.shadowBias = 0
        self.shadowRadius = 1
        self.shadowMapSize = Vector2()


class _PointLightUniforms(_LightUniforms):
    def __init__(self):
        super().__init__()
        self.position = Vector3()
        self.color = Color()
        self.distance = 0
        self.decay = 0

        self.shadow = False
        self.shadowBias = 0
        self.shadowRadius = 1
        self.shadowMapSize = Vector2()
        self.shadowCameraNear = 1
        self.shadowCameraFar = 1000


class _HemisphereLightUniforms(_LightUniforms):
    def __init__(self):
        super().__init__()
        self.direction = Vector3()
        self.skyColor = Color()
        self.groundColor = Color()


class _RectAreaLightUniforms(_LightUniforms):
    def __init__(self):
        super().__init__()
        self.color = Color()
        self.position = Vector3()
        self.halfWidth = Vector3()
        self.halfHeight = Vector3()
        # // TODO (abelnation): set RectAreaLight shadow uniforms


class _UniformsCache:
    def __init__(self):
        self.lights = {}

    def get(self, light):
        if light.id  in self.lights:
            return self.lights[ light.id ]

        if light.type == 'DirectionalLight':
                uniforms = _DirectionalLightUniforms()
        elif light.type == 'SpotLight':
                uniforms = _SpotLightUniforms()
        elif light.type == 'PointLight':
                uniforms = _PointLightUniforms()
        elif light.type == 'HemisphereLight':
                uniforms = _HemisphereLightUniforms()
        elif light.type == 'RectAreaLight':
                uniforms = _RectAreaLightUniforms()

        self.lights[ light.id ] = uniforms
        return uniforms


class LightHash:
    def __init__(self):
        self.stateID = -1
        self.directionalLength = -1
        self.pointLength = -1
        self.spotLength = -1
        self.rectAreaLength = -1
        self.hemiLength = -1
        self.shadowsLength = -1


_countLights = 0


class _state:
    def __init__(self):
        global _countLights

        self.id = _countLights
        _countLights += 1
        self.hash = LightHash()

        self.ambient = Color(0, 0, 0)
        self.directional = []
        self.directionalShadowMap = []
        self.directionalShadowMatrix = []
        self.spot = []
        self.spotShadowMap = []
        self.spotShadowMatrix = []
        self.rectArea = []
        self.point = []
        self.pointShadowMap = []
        self.pointShadowMatrix = []
        self.hemi = []


_vector3 = Vector3()
_matrix4 = Matrix4()
_matrix42 = Matrix4()


class pyOpenGLLights:
    def __init__(self):
        self.cache = _UniformsCache()
        self.state = _state()
        # reusable variable

    def setup(self, lights, shadows, camera ):
        global _vector3, _matrix4, _matrix42

        r = 0
        g = 0
        b = 0

        directionalLength = 0
        pointLength = 0
        spotLength = 0
        rectAreaLength = 0
        hemiLength = 0

        self.state.directional.clear()
        self.state.directionalShadowMap.clear()
        self.state.directionalShadowMatrix.clear()
        self.state.point.clear()
        self.state.pointShadowMap.clear()
        self.state.pointShadowMatrix.clear()
        self.state.spot.clear()
        self.state.spotShadowMap.clear()
        self.state.spotShadowMatrix.clear()
        self.state.rectArea.clear()
        self.state.hemi.clear()

        viewMatrix = camera.matrixWorldInverse

        for light in lights:
            color = light.color
            intensity = light.intensity
            distance = light.distance

            shadowMap = light.shadow.map.texture if (light.shadow and light.shadow.map ) else None

            if light.my_class(isAmbientLight):
                r += color.r * intensity
                g += color.g * intensity
                b += color.b * intensity

            elif light.my_class(isDirectionalLight):
                uniforms = self.cache.get( light )

                uniforms.color.copy( light.color ).multiplyScalar( light.intensity )
                uniforms.direction.setFromMatrixPosition( light.matrixWorld )
                _vector3.setFromMatrixPosition( light.target.matrixWorld )
                uniforms.direction.sub( _vector3 )
                uniforms.direction.transformDirection( viewMatrix )

                uniforms.shadow = light.castShadow

                if light.castShadow:
                    shadow = light.shadow

                    uniforms.shadowBias = shadow.bias
                    uniforms.shadowRadius = shadow.radius
                    uniforms.shadowMapSize = shadow.mapSize

                self.state.directionalShadowMap.append(shadowMap)
                self.state.directionalShadowMatrix.append(light.shadow.matrix)
                self.state.directional.append(uniforms)
                directionalLength += 1

            elif light.my_class(isSpotLight):
                uniforms = self.cache.get( light )

                uniforms.position.setFromMatrixPosition( light.matrixWorld )
                uniforms.position.applyMatrix4( viewMatrix )

                uniforms.color.copy( color ).multiplyScalar( intensity )
                uniforms.distance = distance

                uniforms.direction.setFromMatrixPosition( light.matrixWorld )
                _vector3.setFromMatrixPosition( light.target.matrixWorld )
                uniforms.direction.sub( _vector3 )
                uniforms.direction.transformDirection( viewMatrix )

                uniforms.coneCos = math.cos( light.angle )
                uniforms.penumbraCos = math.cos( light.angle * ( 1 - light.penumbra ) )
                uniforms.decay = 0.0 if ( light.distance == 0 ) else light.decay

                uniforms.shadow = light.castShadow

                if light.castShadow:
                    shadow = light.shadow

                    uniforms.shadowBias = shadow.bias
                    uniforms.shadowRadius = shadow.radius
                    uniforms.shadowMapSize = shadow.mapSize

                self.state.spotShadowMap.append(shadowMap)
                self.state.spotShadowMatrix.append(light.shadow.matrix)
                self.state.spot.append(uniforms)
                spotLength += 1

            elif light.is_a('RectAreaLight'):
                uniforms = self.cache.get( light )

                # (a) intensity is the total visible light emitted
                # uniforms.color.copy(color).multiplyScalar(intensity / (light.width * light.height * Math.PI))

                # // (b) intensity controls the radiance per light area
                uniforms.color.copy( color ).multiplyScalar(intensity)

                uniforms.position.setFromMatrixPosition( light.matrixWorld )
                uniforms.position.applyMatrix4( viewMatrix )

                # // extract local rotation of light to derive width/height half vectors
                _matrix42.identity()
                _matrix4.copy( light.matrixWorld )
                _matrix4.premultiply( viewMatrix )
                _matrix42.extractRotation( _matrix4 )

                uniforms.halfWidth.set( light.width * 0.5,                0.0, 0.0 )
                uniforms.halfHeight.set(              0.0, light.height * 0.5, 0.0 )

                uniforms.halfWidth.applyMatrix4( _matrix42 )
                uniforms.halfHeight.applyMatrix4( _matrix42 )

                # // TODO (abelnation): RectAreaLight distance?
                # // uniforms.distance = distance;

                self.state.rectArea.append(uniforms)
                rectAreaLength += 1

            elif light.my_class(isPointLight):
                uniforms = self.cache.get( light )

                uniforms.position.setFromMatrixPosition( light.matrixWorld )
                uniforms.position.applyMatrix4( viewMatrix )

                uniforms.color.copy( light.color ).multiplyScalar( light.intensity )
                uniforms.distance = light.distance
                uniforms.decay = 0.0 if ( light.distance == 0 ) else light.decay

                uniforms.shadow = light.castShadow

                if light.castShadow:
                    shadow = light.shadow

                    uniforms.shadowBias = shadow.bias
                    uniforms.shadowRadius = shadow.radius
                    uniforms.shadowMapSize = shadow.mapSize
                    uniforms.shadowCameraNear = shadow.camera.near
                    uniforms.shadowCameraFar = shadow.camera.far

                self.state.pointShadowMap.append(shadowMap)
                self.state.pointShadowMatrix.append(light.shadow.matrix)
                self.state.point.append(uniforms)
                pointLength += 1

            elif light.my_class(isHemisphereLight):
                uniforms = self.cache.get( light )

                uniforms.direction.setFromMatrixPosition( light.matrixWorld )
                uniforms.direction.transformDirection( viewMatrix )
                uniforms.direction.normalize()

                uniforms.skyColor.copy( light.color ).multiplyScalar( intensity )
                uniforms.groundColor.copy( light.groundColor ).multiplyScalar( intensity )

                self.state.hemi.append(uniforms)
                hemiLength += 1

        self.state.ambient.r = r
        self.state.ambient.g = g
        self.state.ambient.b = b

        self.state.hash.stateID = self.state.id
        self.state.hash.directionalLength = directionalLength
        self.state.hash.pointLength = pointLength
        self.state.hash.spotLength = spotLength
        self.state.hash.rectAreaLength = rectAreaLength
        self.state.hash.hemiLength = hemiLength
        self.state.hash.shadowsLength = len(shadows)

        return self

    def update_uniform_block(self, uniformBlocks):
        lights_state = self.state
        uniformBlocks.set_value('ambientLightColor', lights_state.ambient)
        uniformBlocks.set_value('directionalLights', lights_state.directional)
        uniformBlocks.set_value('pointLights', lights_state.point)
        uniformBlocks.set_value('spotLights', lights_state.spot)
        uniformBlocks.set_value('rectAreaLights', lights_state.rectArea)
        uniformBlocks.set_value('hemisphereLights', lights_state.hemi)
        uniformBlocks.update('lights')
