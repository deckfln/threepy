"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.Vector2 import *
from THREE.Vector3 import *
from THREE.Matrix4 import *
from THREE.Color import *


class UniformsCache:
    def __init__(self):
        self.lights = {}

    def get(self, light):
        if light.id  in self.lights:
            return self.lights[ light.id ]

        if light.type == 'DirectionalLight':
                uniforms = {
                    'direction': Vector3(),
                    'color': Color(),

                    'shadow': False,
                    'shadowBias': 0,
                    'shadowRadius': 1,
                    'shadowMapSize': Vector2()
                }
        elif light.type == 'SpotLight':
                uniforms = {
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
                }
        elif light.type == 'PointLight':
                uniforms = {
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
                }
        elif light.type == 'HemisphereLight':
                uniforms = {
                    'direction': Vector3(),
                    'skyColor': Color(),
                    'groundColor': Color()
                }
        elif light.type == 'RectAreaLight':
                uniforms = {
                    'color': Color(),
                    'position': Vector3(),
                    'halfWidth': Vector3(),
                    'halfHeight': Vector3()
                    # // TODO (abelnation): set RectAreaLight shadow uniforms
                }

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

    def setup(self, lights, shadows, camera ):
        r = 0
        g = 0
        b = 0

        directionalLength = 0
        pointLength = 0
        spotLength = 0
        rectAreaLength = 0
        hemiLength = 0

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

                self.directionalShadowMap[ directionalLength ] = shadowMap
                self.directionalShadowMatrix[ directionalLength ] = light.shadow.matrix
                self.directional[ directionalLength ] = uniforms

                directionalLength += 1
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

                self.spotShadowMap[ spotLength ] = shadowMap
                self.spotShadowMatrix[ spotLength ] = light.shadow.matrix
                self.spot[ spotLength ] = uniforms

                spotLength += 1
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

                self.rectArea[ rectAreaLength ] = uniforms

                rectAreaLength += 1

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

                self.pointShadowMap[ pointLength ] = shadowMap
                self.pointShadowMatrix[ pointLength ] = light.shadow.matrix
                self.point[ pointLength ] = uniforms

                pointLength += 1
            elif light.isHemisphereLight:
                uniforms = self.cache.get( light )

                uniforms.direction.setFromMatrixPosition( light.matrixWorld )
                uniforms.direction.transformDirection( viewMatrix )
                uniforms.direction.normalize()

                uniforms.skyColor.copy( light.color ).multiplyScalar( intensity )
                uniforms.groundColor.copy( light.groundColor ).multiplyScalar( intensity )

                self.state.hemi[ hemiLength ] = uniforms

                hemiLength += 1

        self.ambient[ 0 ] = r
        self.ambient[ 1 ] = g
        self.ambient[ 2 ] = b

        self.directional.length = directionalLength
        self.spot.length = spotLength
        self.rectArea.length = rectAreaLength
        self.point.length = pointLength
        self.hemi.length = hemiLength

        # // TODO (sam-g-steel) why aren't we using join
        self.hash = "+".join([directionalLength,pointLength,spotLength,rectAreaLength,hemiLength,len(shadows)])

        return self
