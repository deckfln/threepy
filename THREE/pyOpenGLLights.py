"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.Vector2 import *
from THREE.Vector3 import *
from THREE.Matrix4 import *
from THREE.Color import *
from THREE.Javascript import *


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
        self.shadowBias = 0
        self.shadowRadius = 1
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


class _state:
    def __init__(self):
        self.hash = ''

        self.ambient = THREE.Color(0, 0, 0)
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


class pyOpenGLLights:
    def __init__(self):
        self.cache = _UniformsCache()
        self.state = _state()
        # reusable variable
        self.vector3 = Vector3()
        self.matrix4 = Matrix4()
        self.matrix42 = Matrix4()

    def setup(self, lights, shadows, camera ):
        r = 0
        g = 0
        b = 0

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

        vector3 = self.vector3
        matrix4 = self.matrix4
        matrix42 = self.matrix42

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
                vector3.setFromMatrixPosition( light.target.matrixWorld )
                uniforms.direction.sub( vector3 )
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

            elif light.my_class(isSpotLight):
                uniforms = self.cache.get( light )

                uniforms.position.setFromMatrixPosition( light.matrixWorld )
                uniforms.position.applyMatrix4( viewMatrix )

                uniforms.color.copy( color ).multiplyScalar( intensity )
                uniforms.distance = distance

                uniforms.direction.setFromMatrixPosition( light.matrixWorld )
                vector3.setFromMatrixPosition( light.target.matrixWorld )
                uniforms.direction.sub( vector3 )
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

            elif light.is_a('RectAreaLight'):
                uniforms = self.cache.get( light )

                # // (a) intensity controls irradiance of entire light
                uniforms.color.copy( color ).multiplyScalar( intensity / ( light.width * light.height ) )

                # // (b) intensity controls the radiance per light area
                # // uniforms.color.copy( color ).multiplyScalar( intensity );

                uniforms.position.setFromMatrixPosition( light.matrixWorld )
                uniforms.position.applyMatrix4( viewMatrix )

                # // extract local rotation of light to derive width/height half vectors
                matrix42.identity()
                matrix4.copy( light.matrixWorld )
                matrix4.premultiply( viewMatrix )
                matrix42.extractRotation( matrix4 )

                uniforms.halfWidth.set( light.width * 0.5,                0.0, 0.0 )
                uniforms.halfHeight.set(              0.0, light.height * 0.5, 0.0 )

                uniforms.halfWidth.applyMatrix4( matrix42 )
                uniforms.halfHeight.applyMatrix4( matrix42 )

                # // TODO (abelnation): RectAreaLight distance?
                # // uniforms.distance = distance;

                self.state.rectArea.append(uniforms)

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

            elif light.my_class(isHemisphereLight):
                uniforms = self.cache.get( light )

                uniforms.direction.setFromMatrixPosition( light.matrixWorld )
                uniforms.direction.transformDirection( viewMatrix )
                uniforms.direction.normalize()

                uniforms.skyColor.copy( light.color ).multiplyScalar( intensity )
                uniforms.groundColor.copy( light.groundColor ).multiplyScalar( intensity )

                self.state.hemi.append(uniforms)

        self.state.ambient.r = r
        self.state.ambient.g = g
        self.state.ambient.b = b

        # // TODO (sam-g-steel) why aren't we using join
        self.state.hash = "%d+%d+%d+%d+%d+%d" % (len(self.state.directional), len(self.state.point), len(self.state.spot), len(self.state.rectArea), len(self.state.hemi), len(shadows))

        return self
