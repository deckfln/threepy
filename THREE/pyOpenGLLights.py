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


class UniformsCache:
    def __init__(self):
        self.lights = {}

    def get(self, light):
        if light.id  in self.lights:
            return self.lights[ light.id ]

        if light.type == 'DirectionalLight':
                uniforms = javascriptObject({
                    'direction': Vector3(),
                    'color': Color(),

                    'shadow': False,
                    'shadowBias': 0,
                    'shadowRadius': 1,
                    'shadowMapSize': Vector2()
                })
        elif light.type == 'SpotLight':
                uniforms = javascriptObject({
                    'position': Vector3(),
                    'direction': Vector3(),
                    'color': Color(),
                    'distance': 0,
                    'coneCos': 0,
                    'penumbraCos': 0,
                    'decay': 0,

                    'shadow': False,
                    'shadowBias': 0,
                    'shadowRadius': 1,
                    'shadowMapSize': Vector2()
                })
        elif light.type == 'PointLight':
                uniforms = javascriptObject({
                    'position': Vector3(),
                    'color': Color(),
                    'distance': 0,
                    'decay': 0,

                    'shadow': False,
                    'shadowBias': 0,
                    'shadowRadius': 1,
                    'shadowMapSize': Vector2(),
                    'shadowCameraNear': 1,
                    'shadowCameraFar': 1000
                })
        elif light.type == 'HemisphereLight':
                uniforms = javascriptObject({
                    'direction': Vector3(),
                    'skyColor': Color(),
                    'groundColor': Color()
                })
        elif light.type == 'RectAreaLight':
                uniforms = javascriptObject({
                    'color': Color(),
                    'position': Vector3(),
                    'halfWidth': Vector3(),
                    'halfHeight': Vector3()
                    # // TODO (abelnation): set RectAreaLight shadow uniforms
                })

        self.lights[ light.id ] = uniforms
        return uniforms


class _state:
    def __init__(self):
        self.hash = ''

        self.ambient = [0, 0, 0]
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
        self.cache = UniformsCache()
        self.state = _state()

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

        vector3 = Vector3()
        matrix4 = Matrix4()
        matrix42 = Matrix4()

        for i in range(len(lights)):
            light = lights[ i ]

            color = light.color
            intensity = light.intensity
            distance = light.distance

            shadowMap = light.shadow.map.texture if (light.shadow and light.shadow.map ) else None

            if light.isAmbientLight:
                r += color.r * intensity
                g += color.g * intensity
                b += color.b * intensity
            elif light.isDirectionalLight:
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
            elif light.isSpotLight:
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
            elif light.isRectAreaLight:
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

            elif light.isPointLight:
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
            elif light.isHemisphereLight:
                uniforms = self.cache.get( light )

                uniforms.direction.setFromMatrixPosition( light.matrixWorld )
                uniforms.direction.transformDirection( viewMatrix )
                uniforms.direction.normalize()

                uniforms.skyColor.copy( light.color ).multiplyScalar( intensity )
                uniforms.groundColor.copy( light.groundColor ).multiplyScalar( intensity )

                self.state.hemi.append(uniforms)

        self.state.ambient[ 0 ] = r
        self.state.ambient[ 1 ] = g
        self.state.ambient[ 2 ] = b

        # // TODO (sam-g-steel) why aren't we using join
        self.state.hash = "%d+%d+%d+%d+%d+%d" % (len(self.state.directional), len(self.state.point), len(self.state.spot), len(self.state.rectArea), len(self.state.hemi), len(shadows))

        return self
