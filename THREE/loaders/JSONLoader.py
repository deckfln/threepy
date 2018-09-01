"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author alteredq / http:# //alteredqualia.com/
 */
"""
import json as JSON

from THREE.loaders.Loader import *
from THREE.core.Geometry import *
from THREE.MorphTarget import *
from THREE.animation.AnimationClip import *


class JSONLoader:
    def __init__(self, manager=None ):

        if isinstance(manager, bool):
            print( 'THREE.JSONLoader: showStatus parameter has been removed from constructor.' )
            manager = None

        self.manager = manager if ( manager is not None ) else DefaultLoadingManager
        self.texturePath = None
        self.withCredentials = False

    def load(self, url, onLoad, onProgress=None, onError=None ):
        texturePath = self.texturePath if self.texturePath and ( isinstance(self.texturePath, str)) else Loader.extractUrlBase( url )

        loader = FileLoader( self.manager )
        loader.setWithCredentials( self.withCredentials )
        
        def _loader(text):
            json = JSON.loads( text )
            if 'metadata' in json:
                metadata = json['metadata']

                if 'type' in metadata:
                    type = metadata['type']
                    if type.tolower() == 'object':
                        raise RuntimeError( 'THREE.JSONLoader: ' + url + ' should be loaded with THREE.ObjectLoader instead.' )

            object = self.parse( json, texturePath )
            onLoad( object['geometry'], object['materials'] )

        return loader.load( url, _loader, onProgress, onError )

    def setTexturePath(self, value ):
        self.texturePath = value
        return self

    def parse(self, json, texturePath):

        def parseModel( json, geometry ):
            def isBitSet( value, position ):
                return value & ( 1 << position )

            faces = json['faces']
            vertices = json['vertices']
            normals = json['normals']
            colors = json['colors']

            scale = json['scale']

            nUvLayers = 0

            if 'uvs' in json:
                # // disregard empty arrays

                for i in range(len(json['uvs'])):
                    if len(json['uvs'][ i ]):
                        nUvLayers += 1

                for i in range(nUvLayers):
                    geometry.faceVertexUvs[ i ] = []

            offset = 0
            zLength = len(vertices)

            while offset < zLength:
                vertex = Vector3()

                vertex.x = vertices[ offset ] * scale
                vertex.y = vertices[ offset + 1 ] * scale
                vertex.z = vertices[ offset + 2 ] * scale
                offset += 3

                geometry.vertices.append( vertex )

            offset = 0
            zLength = len(faces)

            while offset < zLength:
                type = faces[ offset ]
                offset += 1

                isQuad = isBitSet( type, 0 )
                hasMaterial = isBitSet( type, 1 )
                hasFaceVertexUv = isBitSet( type, 3 )
                hasFaceNormal = isBitSet( type, 4 )
                hasFaceVertexNormal = isBitSet( type, 5 )
                hasFaceColor = isBitSet( type, 6 )
                hasFaceVertexColor = isBitSet( type, 7 )

                # // console.log("type", type, "bits", isQuad, hasMaterial, hasFaceVertexUv, hasFaceNormal, hasFaceVertexNormal, hasFaceColor, hasFaceVertexColor)

                if isQuad:
                    faceA = Face3()
                    faceA.a = faces[ offset ]
                    faceA.b = faces[ offset + 1 ]
                    faceA.c = faces[ offset + 3 ]

                    faceB = Face3()
                    faceB.a = faces[ offset + 1 ]
                    faceB.b = faces[ offset + 2 ]
                    faceB.c = faces[ offset + 3 ]

                    offset += 4

                    if hasMaterial:
                        materialIndex = faces[ offset ]
                        faceA.materialIndex = materialIndex
                        faceB.materialIndex = materialIndex
                        offset += 1
                        
                    # // to get face <=> uv index correspondence

                    fi = len(geometry.faces)

                    if hasFaceVertexUv:
                        for i in range(nUvLayers):
                            uvLayer = json.uvs[ i ]

                            geometry.faceVertexUvs[ i ][ fi ] = []
                            geometry.faceVertexUvs[ i ][ fi + 1 ] = []

                            for j in range(4):
                                uvIndex = faces[ offset ]
                                offset += 1

                                u = uvLayer[ uvIndex * 2 ]
                                v = uvLayer[ uvIndex * 2 + 1 ]

                                uv = Vector2( u, v )

                                if j != 2:
                                    geometry.faceVertexUvs[ i ][ fi ].append( uv )
                                if j != 0:
                                    geometry.faceVertexUvs[ i ][ fi + 1 ].append( uv )

                    if hasFaceNormal:
                        normalIndex = faces[ offset ] * 3
                        offset += 1

                        faceA.normal.set(
                            normals[ normalIndex ],
                            normals[ normalIndex + 1 ],
                            normals[ normalIndex + 2]
                        )
                        normalIndex += 3

                        faceB.normal.copy( faceA.normal )

                    if hasFaceVertexNormal:
                        for i in range(4):
                            normalIndex = faces[ offset ] * 3
                            offset += 1
                            normal = Vector3(
                                normals[ normalIndex ],
                                normals[ normalIndex + 1],
                                normals[ normalIndex + 2]
                            )
                            normalIndex += 3

                            if i != 2:
                                faceA.vertexNormals.append( normal )
                            if i != 0:
                                faceB.vertexNormals.append( normal )


                    if hasFaceColor:
                        colorIndex = faces[ offset ]
                        offset += 1
                        hex = colors[ colorIndex ]

                        faceA.color.setHex( hex )
                        faceB.color.setHex( hex )

                    if hasFaceVertexColor:
                        for i in range(4):
                            colorIndex = faces[ offset ]
                            offset += 1
                            hex = colors[ colorIndex ]

                            if i != 2:
                                faceA.vertexColors.append( Color( hex ) )
                            if i != 0:
                                faceB.vertexColors.append( Color( hex ) )

                    geometry.faces.append( faceA )
                    geometry.faces.append( faceB )

                else:
                    face = Face3()
                    face.a = faces[ offset ]
                    face.b = faces[ offset + 1 ]
                    face.c = faces[ offset + 2 ]
                    
                    offset += 3

                    if hasMaterial:
                        materialIndex = faces[ offset ]
                        offset += 1
                        face.materialIndex = materialIndex

                    # // to get face <=> uv index correspondence

                    fi = len(geometry.faces)

                    if hasFaceVertexUv:
                        for i in range(nUvLayers):
                            uvLayer = json['uvs'][ i ]

                            geometry.faceVertexUvs[ i ].append([])

                            for j in range(3):
                                uvIndex = faces[ offset ]
                                offset += 1

                                u = uvLayer[ uvIndex * 2 ]
                                v = uvLayer[ uvIndex * 2 + 1 ]

                                uv = Vector2( u, v )

                                geometry.faceVertexUvs[ i ][ fi ].append( uv )

                    if hasFaceNormal:
                        normalIndex = faces[ offset ] * 3
                        offset += 1
                        
                        face.normal.set(
                            normals[ normalIndex ],
                            normals[ normalIndex + 1 ],
                            normals[ normalIndex + 2]
                        )
                        normalIndex += 3

                    if hasFaceVertexNormal:
                        for i in range(3):
                            normalIndex = faces[ offset ] * 3
                            offset += 1
                            
                            normal = Vector3(
                                normals[ normalIndex ],
                                normals[ normalIndex + 1],
                                normals[ normalIndex + 2]
                            )
                            normalIndex += 3

                            face.vertexNormals.append( normal )

                    if hasFaceColor:
                        colorIndex = faces[ offset ]
                        offset += 1
                        face.color.setHex( colors[ colorIndex ] )

                    if hasFaceVertexColor:
                        for i in range(3):
                            colorIndex = faces[ offset ]
                            offset += 1
                            face.vertexColors.append( Color( colors[ colorIndex ] ) )

                    geometry.faces.append( face )

        def parseSkin( json, geometry ):
            influencesPerVertex = json['influencesPerVertex'] if ( 'influencesPerVertex' in json ) else 2

            if 'skinWeights' in json:
                skinWeights = json['skinWeights']
                for i in range(0, len(skinWeights), influencesPerVertex ):
                    x = skinWeights[ i ]
                    y = skinWeights[ i + 1 ] if ( influencesPerVertex > 1 ) else 0
                    z = skinWeights[ i + 2 ] if ( influencesPerVertex > 2 ) else 0
                    w =  skinWeights[ i + 3 ] if ( influencesPerVertex > 3 ) else 0

                    geometry.skinWeights.append( Vector4( x, y, z, w ) )

            if 'skinIndices' in json:
                skinIndices = json['skinIndices']
                for i in range (0, len(skinIndices), influencesPerVertex ):
                    a = skinIndices[ i ]
                    b = skinIndices[ i + 1 ] if ( influencesPerVertex > 1 ) else 0
                    c = skinIndices[ i + 2 ] if ( influencesPerVertex > 2 ) else 0
                    d = skinIndices[ i + 3 ] if ( influencesPerVertex > 3 ) else 0

                    geometry.skinIndices.append( Vector4( a, b, c, d ) )

            if 'bones' in json:
                geometry.bones = json['bones']

            if geometry.bones and len(geometry.bones) > 0 and ( len(geometry.skinWeights) != len(geometry.skinIndices) or len(geometry.skinIndices) != len(geometry.vertices) ):
                print( 'When skinning, number of vertices (' + geometry.vertices.length + '), skinIndices (' +
                    geometry.skinIndices.length + '), and skinWeights (' + geometry.skinWeights.length + ') should match.' )


        def parseMorphing( json, geometry ):
            scale = json['scale']

            if 'morphTargets' in json:
                morphTargets = json['morphTargets']
                for i in range(len(morphTargets)):
                    geometry.morphTargets.append(MorphTarget())
                    geometry.morphTargets[ i ].name = morphTargets[ i ]['name']
                    geometry.morphTargets[ i ].vertices = []

                    dstVertices = geometry.morphTargets[ i ].vertices
                    srcVertices = morphTargets[ i ]['vertices']

                    for v in range(0, len(srcVertices), 3 ):
                        vertex = Vector3()
                        vertex.x = srcVertices[ v ] * scale
                        vertex.y = srcVertices[ v + 1 ] * scale
                        vertex.z = srcVertices[ v + 2 ] * scale

                        dstVertices.append( vertex )

            if 'morphColors' in json and len(json['morphColors']) > 0:
                print( 'THREE.JSONLoader: "morphColors" no longer supported. Using them as face colors.' )

                faces = geometry.faces
                morphColors = json['morphColors'][ 0 ]['colors']

                for i in range(len(faces)):
                    faces[ i ].color.fromArray( morphColors, i * 3 )

        def parseAnimations( json, geometry ):
            outputAnimations = []

            # // parse old style Bone/Hierarchy animations
            animations = []

            if 'animation' in json:
                animations.append( json['animation'] )

            if 'animations' in json:
                if len(json['animations']):
                    animations += json['animations']

                else:
                    animations.append( json['animations'] )

            for i in range(len(animations)):
                clip = AnimationClip.parseAnimation( animations[ i ], geometry.bones )
                if clip:
                    outputAnimations.append( clip )

            # // parse implicit morph animations
            if geometry.morphTargets:
                # // TODO: Figure out what an appropraite FPS is for morph target animations -- defaulting to 10, but really it is completely arbitrary.
                morphAnimationClips = AnimationClip.CreateClipsFromMorphTargetSequences( geometry.morphTargets, 10 )
                outputAnimations += morphAnimationClips

            if len(outputAnimations) > 0:
                geometry.animations = outputAnimations

        if 'data' in json:
            # // Geometry 4.0 spec
            json = json['data']

        if 'scale' in json:
            json['scale'] = 1.0 / json['scale']

        else:
            json['scale'] = 1.0

        geometry = Geometry()

        parseModel( json, geometry )
        parseSkin( json, geometry )
        parseMorphing( json, geometry )
        parseAnimations( json, geometry )

        geometry.computeFaceNormals()
        geometry.computeBoundingSphere()

        if 'materials' not in json or len(json['materials']) == 0:
            return { 'geometry': geometry, 'materials': None }

        else:
            materials = Loader.initMaterials( json['materials'], texturePath, True )
            return { 'geometry': geometry, 'materials': materials }
