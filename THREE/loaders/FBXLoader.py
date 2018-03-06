"""
 * @author Kyle-Larson https:#github.com/Kyle-Larson
 * @author Takahiro https:#github.com/takahirox
 *
 * Loader loads FBX file and generates Group representing FBX scene.
 * Requires FBX file to be >= 7.0 and in ASCII or to be any version in Binary format.
 *
 * Supports:
 *     Mesh Generation (Positional Data)
 *     Normal Data (Per Vertex Drawing Instance)
 *  UV Data (Per Vertex Drawing Instance)
 *  Skinning
 *  Animation
 *     - Separated Animations based on stacks.
 *     - Skeletal & Non-Skeletal Animations
 *  NURBS (Open, Closed and Periodic forms)
 *
 * Needs Support:
 *     Indexed Buffers
 *     PreRotation support.
"""

"""
 * Generates a loader for loading FBX files from URL and parsing into
 * a THREE.Group.
 * @param {THREE.LoadingManager} manager - Loading Manager for loader to use.
"""
class FBXLoader:
    def __init__(self, manager=None):
        self.manager = manager if manager is not None ) else THREE.DefaultLoadingManager

    """
     * Loads an ASCII/Binary FBX file from URL and parses into a THREE.Group.
     * THREE.Group will have an animations property of AnimationClips
     * of the different animations exported with the FBX.
     * @param {string} url - URL of the FBX file.
     * @param {function(THREE.Group):void} onLoad - Callback for when FBX file is loaded and parsed.
     * @param {function(ProgressEvent):void} onProgress - Callback fired periodically when file is being retrieved from server.
     * @param {function(Event):void} onError - Callback fired when error occurs (Currently only with retrieving file, not with parsing errors).
    """
    def load(self, url, onLoad, onProgress, onError ):
        resourceDirectory = THREE.Loader.prototype.extractUrlBase( url )

        loader = THREE.FileLoader( self.manager )
        loader.setResponseType( 'arraybuffer' )
        loader.load( url, def ( buffer ):

        try:
            scene = self.parse( buffer, resourceDirectory )
            onLoad( scene )

        catch:
            window.setTimeout( def ():
                if onError ) onError( error )
                self.manager.itemError( url )
            }, 0 )
        }

    """
     * Parses an ASCII/Binary FBX file and returns a THREE.Group.
     * THREE.Group will have an animations property of AnimationClips
     * of the different animations within the FBX file.
     * @param {ArrayBuffer} FBXBuffer - Contents of FBX file to parse.
     * @param {string} resourceDirectory - Directory to load external assets (e.g. textures ) from.
     * @returns {THREE.Group}
    """
    def parse(self, FBXBuffer, resourceDirectory ):

        if isFbxFormatBinary( FBXBuffer ):
            FBXTree = BinaryParser().parse( FBXBuffer )
        else:
            FBXText = convertArrayBufferToString( FBXBuffer )

            if not isFbxFormatASCII( FBXText ):
                raise RuntimeError( 'THREE.FBXLoader: Unknown format.' )

            if getFbxVersion( FBXText ) < 7000:
                raise RuntimeError( 'THREE.FBXLoader: FBX version not supported, FileVersion: ' + getFbxVersion( FBXText ) )

            FBXTree = TextParser().parse( FBXText )

        # console.log( FBXTree )

        connections = parseConnections( FBXTree )
        images = parseImages( FBXTree )
        textures = parseTextures( FBXTree, THREE.TextureLoader( self.manager ).setPath( resourceDirectory ), images, connections )
        materials = parseMaterials( FBXTree, textures, connections )
        deformers = parseDeformers( FBXTree, connections )
        geometryMap = parseGeometries( FBXTree, connections, deformers )
        sceneGraph = parseScene( FBXTree, connections, deformers, geometryMap, materials )

        return sceneGraph

"""
 * Parses map of relationships between objects.
 * @param {{Connections: { properties: { connections: [number, number, string][]}}}} FBXTree
 * @returns {Map<number, {parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}>}
"""
def parseConnections( FBXTree ):

    """
     * @type {Map<number, { parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}>}
    """
    connectionMap = Map()

    if 'Connections' in FBXTree:
        """
         * @type {[number, number, string][]}
        """
        connectionArray = FBXTree.Connections.properties.connections
        for connectionArrayIndex in range(len(connectionArray)):
            connection = connectionArray[ connectionArrayIndex ]

            if not connectionMap.has( connection[ 0 ] ):
                connectionMap.set( connection[ 0 ], {
                    parents: [],
                    children: []
                } )

            parentRelationship = { 'ID': connection[ 1 ], 'relationship': connection[ 2 ] }
            connectionMap.get( connection[ 0 ] ).parents.append( parentRelationship )

            if not connectionMap.has( connection[ 1 ] ):
                connectionMap.set( connection[ 1 ], {
                    parents: [],
                    children: []
                } )

            childRelationship = { 'ID': connection[ 0 ], 'relationship': connection[ 2 ] }
            connectionMap.get( connection[ 1 ] ).children.append( childRelationship )


    return connectionMap

"""
 * Parses map of images referenced in FBXTree.
 * @param {{Objects: {subNodes: {Texture: Object.<string, FBXTextureNode>}}}} FBXTree
 * @returns {Map<number, string(image blob/data URL)>}
"""
def parseImages( FBXTree ):
    """
     * @type {Map<number, string(image blob/data URL)>}
    """
    imageMap = Map()

    if 'Video' in FBXTree.Objects.subNodes:
        videoNodes = FBXTree.Objects.subNodes.Video

        for nodeID in videoNodes:
            videoNode = videoNodes[ nodeID ]

            # raw image data is in videoNode.properties.Content
            if 'Content' in videoNode.properties:
                image = parseImage( videoNodes[ nodeID ] )
                imageMap.set( parseInt( nodeID ), image )

    return imageMap

"""
 * @param {videoNode} videoNode - Node to get texture image information from.
 * @returns {string} - image blob/data URL
"""
def parseImage( videoNode ):
    content = videoNode.properties.Content
    fileName = videoNode.properties.RelativeFilename || videoNode.properties.Filename
    extension = fileName.slice( fileName.lastIndexOf( '.' ) + 1 ).toLowerCase()

    if extension == 'bmp':
            type = 'image/bmp'
    elif extension == 'jpg':
            type = 'image/jpeg'
    elif extension == 'png':
            type = 'image/png'
    elif extension == 'tif':
            type = 'image/tiff'
    else:
            print( 'FBXLoader: No support image type ' + extension )
            return

    if typeof content == 'string':
        return 'data:' + type + ';base64,' + content
    else:
        array = Uint8Array( content )
        return window.URL.createObjectURL( Blob( [ array ], { type: type } ) )

"""
 * Parses map of textures referenced in FBXTree.
 * @param {{Objects: {subNodes: {Texture: Object.<string, FBXTextureNode>}}}} FBXTree
 * @param {THREE.TextureLoader} loader
 * @param {Map<number, string(image blob/data URL)>} imageMap
 * @param {Map<number, {parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}>} connections
 * @returns {Map<number, THREE.Texture>}
"""
def parseTextures( FBXTree, loader, imageMap, connections ):
    """
     * @type {Map<number, THREE.Texture>}
    """
    textureMap = Map()

    if 'Texture' in FBXTree.Objects.subNodes:
        textureNodes = FBXTree.Objects.subNodes.Texture
        for nodeID in textureNodes:
            texture = parseTexture( textureNodes[ nodeID ], loader, imageMap, connections )
            textureMap.set( parseInt( nodeID ), texture )

    return textureMap

"""
 * @param {textureNode} textureNode - Node to get texture information from.
 * @param {THREE.TextureLoader} loader
 * @param {Map<number, string(image blob/data URL)>} imageMap
 * @param {Map<number, {parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}>} connections
 * @returns {THREE.Texture}
"""
def parseTexture( textureNode, loader, imageMap, connections ):
    FBX_ID = textureNode.id

    name = textureNode.name

    filePath = textureNode.properties.FileName
    relativeFilePath = textureNode.properties.RelativeFilename

    children = connections.get( FBX_ID ).children

    if children is not None and children.length > 0 and imageMap.has( children[ 0 ].ID ):
        fileName = imageMap.get( children[ 0 ].ID )
    elif relativeFilePath is not None and relativeFilePath[ 0 ] !== '/' and relativeFilePath.match( /^[a-zA-Z]:/ ) is None:
        # use textureNode.properties.RelativeFilename
        # if it exists and it doesn't seem an absolute path
        fileName = relativeFilePath
    else:
        split = filePath.split( /[\\\/]/ )

        if len(split) > 0:
            fileName = split[ len(split) - 1 ]
        else:
            fileName = filePath

    currentPath = loader.path

    if fileName.indexOf( 'blob:' ) == 0 || fileName.indexOf( 'data:' ) == 0:
        loader.setPath( undefined )

    """
     * @type {THREE.Texture}
    """
    texture = loader.load( fileName )
    texture.name = name
    texture.FBX_ID = FBX_ID

    wrapModeU = textureNode.properties.WrapModeU
    wrapModeV = textureNode.properties.WrapModeV

    valueU = wrapModeU if wrapModeU is not None else 0
    valueV = wrapModeV.value wrapModeV is not None else 0

    # http:#download.autodesk.com/us/fbx/SDKdocs/FBX_SDK_Help/files/fbxsdkref/class_k_fbx_texture.html#889640e63e2e681259ea81061b85143a
    # 0: repeat(default), 1: clamp

    texture.wrapS = THREE.RepeatWrapping if valueU == 0 else THREE.ClampToEdgeWrapping
    texture.wrapT = THREE.RepeatWrapping if valueV == 0 else THREE.ClampToEdgeWrapping

    loader.setPath( currentPath )

    return texture

"""
 * Parses map of Material information.
 * @param {{Objects: {subNodes: {Material: Object.<number, FBXMaterialNode>}}}} FBXTree
 * @param {Map<number, THREE.Texture>} textureMap
 * @param {Map<number, {parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}>} connections
 * @returns {Map<number, THREE.Material>}
"""
def parseMaterials( FBXTree, textureMap, connections ):
    materialMap = Map()

    if 'Material' in FBXTree.Objects.subNodes:
        materialNodes = FBXTree.Objects.subNodes.Material
        for nodeID in materialNodes:
            material = parseMaterial( materialNodes[ nodeID ], textureMap, connections )
            materialMap.set( parseInt( nodeID ), material )

    return materialMap

"""
 * Takes information from Material node and returns a generated THREE.Material
 * @param {FBXMaterialNode} materialNode
 * @param {Map<number, THREE.Texture>} textureMap
 * @param {Map<number, {parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}>} connections
 * @returns {THREE.Material}
"""
def parseMaterial( materialNode, textureMap, connections ):

    FBX_ID = materialNode.id
    name = materialNode.attrName
    type = materialNode.properties.ShadingModel

    #Case where FBXs wrap shading model in property object.
    if typeof type == 'object':
        type = type.value

    children = connections.get( FBX_ID ).children

    parameters = parseParameters( materialNode.properties, textureMap, children )

    t = type.lcase()
    if t == 'phong':
            material = THREE.MeshPhongMaterial()
    elif t == 'lambert':
            material = THREE.MeshLambertMaterial()
    else:
            print( 'THREE.FBXLoader: No implementation given for material type %s in FBXLoader.js. Defaulting to basic material.', type )
            material = THREE.MeshBasicMaterial( { color: 0x3300ff } )

    material.setValues( parameters )
    material.name = name

    return material

"""
 * @typedef {{Diffuse: FBXVector3, Specular: FBXVector3, Shininess: FBXValue, Emissive: FBXVector3, EmissiveFactor: FBXValue, Opacity: FBXValue}} FBXMaterialProperties
"""
"""
 * @typedef {{color: THREE.Color=, specular: THREE.Color=, shininess: number=, emissive: THREE.Color=, emissiveIntensity: number=, opacity: number=, transparent: boolean=, map: THREE.Texture=}} THREEMaterialParameterPack
"""
"""
 * @param {FBXMaterialProperties} properties
 * @param {Map<number, THREE.Texture>} textureMap
 * @param {{ID: number, relationship: string}[]} childrenRelationships
 * @returns {THREEMaterialParameterPack}
"""
def parseParameters( properties, textureMap, childrenRelationships ):
    parameters = {}

    if properties.Diffuse:
        parameters.color = parseColor( properties.Diffuse )
        
    if properties.Specular:
        parameters.specular = parseColor( properties.Specular )

    if properties.Shininess:
        parameters.shininess = properties.Shininess.value

    if properties.Emissive:
        parameters.emissive = parseColor( properties.Emissive )

    if properties.EmissiveFactor:
        parameters.emissiveIntensity = properties.EmissiveFactor.value

    if properties.Opacity:
        parameters.opacity = properties.Opacity.value

    if parameters.opacity < 1.0:
        parameters.transparent = true

    for childrenRelationshipsIndex in range(len(childrenRelationships)):
        relationship = childrenRelationships[ childrenRelationshipsIndex ]

        type = relationship.relationship

        if type == 'DiffuseColor' or type==' "DiffuseColor':
            parameters.map = textureMap.get( relationship.ID )

        elif type =='Bump' or type==' "Bump':
            parameters.bumpMap = textureMap.get( relationship.ID )

        elif type=='NormalMap' or type==' "NormalMap':
            parameters.normalMap = textureMap.get( relationship.ID )

        elif type=='AmbientColor' or type=='EmissiveColor' or type==' "AmbientColor' or type==' "EmissiveColor':
            print('THREE.FBXLoader: Unknown texture application of type %s, skipping texture.', type)

        else:
            print( 'THREE.FBXLoader: Unknown texture application of type %s, skipping texture.', type )

    return parameters

"""
 * Generates map of Skeleton-like objects for use later when generating and binding skeletons.
 * @param {{Objects: {subNodes: {Deformer: Object.<number, FBXSubDeformerNode>}}}} FBXTree
 * @param {Map<number, {parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}>} connections
 * @returns {Map<number, {map: Map<number, {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}>, array: {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}[], skeleton: THREE.Skeleton|null}>}
"""
def parseDeformers( FBXTree, connections ):
    deformers = {}

    if 'Deformer' in FBXTree.Objects.subNodes:
        DeformerNodes = FBXTree.Objects.subNodes.Deformer

        for nodeID in DeformerNodes:
            deformerNode = DeformerNodes[ nodeID ]

            if deformerNode.attrType == 'Skin':
                conns = connections.get( parseInt( nodeID ) )
                skeleton = parseSkeleton( conns, DeformerNodes )
                skeleton.FBX_ID = parseInt( nodeID )

                deformers[ nodeID ] = skeleton

    return deformers

"""
 * Generates a "Skeleton Representation" of FBX nodes based on an FBX Skin Deformer's connections and an object containing SubDeformer nodes.
 * @param {{parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}} connections
 * @param {Object.<number, FBXSubDeformerNode>} DeformerNodes
 * @returns {{map: Map<number, {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}>, array: {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}[], skeleton: THREE.Skeleton|null}}
"""
def parseSkeleton( connections, DeformerNodes ):
    subDeformers = {}
    children = connections.children

    for i in range(len(children)):
        child = children[ i ]

        subDeformerNode = DeformerNodes[ child.ID ]

        subDeformer = {
            FBX_ID: child.ID,
            index: i,
            indices: [],
            weights: [],
            transform: parseMatrixArray( subDeformerNode.subNodes.Transform.properties.a ),
            transformLink: parseMatrixArray( subDeformerNode.subNodes.TransformLink.properties.a ),
            linkMode: subDeformerNode.properties.Mode
        }

        if 'Indexes' in subDeformerNode.subNode:
            subDeformer.indices = parseIntArray( subDeformerNode.subNodes.Indexes.properties.a )
            subDeformer.weights = parseFloatArray( subDeformerNode.subNodes.Weights.properties.a )

        subDeformers[ child.ID ] = subDeformer

    return {
        map: subDeformers,
        bones: []
    }

"""
 * Generates Buffer geometries from geometry information in FBXTree, and generates map of THREE.BufferGeometries
 * @param {{Objects: {subNodes: {Geometry: Object.<number, FBXGeometryNode}}}} FBXTree
 * @param {Map<number, {parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}>} connections
 * @param {Map<number, {map: Map<number, {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}>, array: {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}[], skeleton: THREE.Skeleton|null}>} deformers
 * @returns {Map<number, THREE.BufferGeometry>}
"""
def parseGeometries( FBXTree, connections, deformers ):
    geometryMap = Map()

    if 'Geometry' in FBXTree.Objects.subNodes:
        geometryNodes = FBXTree.Objects.subNodes.Geometry

        for nodeID in geometryNodes:
            relationships = connections.get( parseInt( nodeID ) )
            geo = parseGeometry( geometryNodes[ nodeID ], relationships, deformers )
            geometryMap.set( parseInt( nodeID ), geo )

    return geometryMap

"""
 * Generates BufferGeometry from FBXGeometryNode.
 * @param {FBXGeometryNode} geometryNode
 * @param {{parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}} relationships
 * @param {Map<number, {map: Map<number, {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}>, array: {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}[]}>} deformers
 * @returns {THREE.BufferGeometry}
"""
def parseGeometry( geometryNode, relationships, deformers ):
    switch ( geometryNode.attrType ):

        case 'Mesh':
            return parseMeshGeometry( geometryNode, relationships, deformers )
            break

        case 'NurbsCurve':
            return parseNurbsGeometry( geometryNode )
            break

    }

}

"""
 * Specialty def for parsing Mesh based Geometry Nodes.
 * @param {FBXGeometryNode} geometryNode
 * @param {{parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}} relationships - Object representing relationships between specific geometry node and other nodes.
 * @param {Map<number, {map: Map<number, {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}>, array: {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}[]}>} deformers - Map object of deformers and subDeformers by ID.
 * @returns {THREE.BufferGeometry}
"""
def parseMeshGeometry( geometryNode, relationships, deformers ):

    for ( i = 0; i < relationships.children.length; ++ i ):

        deformer = deformers[ relationships.children[ i ].ID ]
        if deformer is not None ) break

    }

    return genGeometry( geometryNode, deformer )

}

"""
 * @param {{map: Map<number, {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}>, array: {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}[]}} deformer - Skeleton representation for geometry instance.
 * @returns {THREE.BufferGeometry}
"""
def genGeometry( geometryNode, deformer ):

    geometry = Geometry()

    subNodes = geometryNode.subNodes

    # First, each index is going to be its own vertex.

    vertexBuffer = parseFloatArray( subNodes.Vertices.properties.a )
    indexBuffer = parseIntArray( subNodes.PolygonVertexIndex.properties.a )

    if subNodes.LayerElementNormal ):

        normalInfo = getNormals( subNodes.LayerElementNormal[ 0 ] )

    }

    if subNodes.LayerElementUV ):

        uvInfo = getUVs( subNodes.LayerElementUV[ 0 ] )

    }

    if subNodes.LayerElementColor ):

        colorInfo = getColors( subNodes.LayerElementColor[ 0 ] )

    }

    if subNodes.LayerElementMaterial ):

        materialInfo = getMaterials( subNodes.LayerElementMaterial[ 0 ] )

    }

    weightTable = {}

    if deformer ):

        subDeformers = deformer.map

        for ( key in subDeformers ):

            subDeformer = subDeformers[ key ]
            indices = subDeformer.indices

            for ( j = 0; j < indices.length; j ++ ):

                index = indices[ j ]
                weight = subDeformer.weights[ j ]

                if weightTable[ index ] == undefined ) weightTable[ index ] = []

                weightTable[ index ].append( {
                    id: subDeformer.index,
                    weight: weight
                } )

            }

        }

    }

    faceVertexBuffer = []
    polygonIndex = 0
    displayedWeightsWarning = false

    for ( polygonVertexIndex = 0; polygonVertexIndex < indexBuffer.length; polygonVertexIndex ++ ):

        vertexIndex = indexBuffer[ polygonVertexIndex ]

        endOfFace = false

        if vertexIndex < 0 ):

            vertexIndex = vertexIndex ^ - 1
            indexBuffer[ polygonVertexIndex ] = vertexIndex
            endOfFace = true

        }

        vertex = Vertex()
        weightIndices = []
        weights = []

        vertex.position.fromArray( vertexBuffer, vertexIndex * 3 )

        if deformer ):

            if weightTable[ vertexIndex ] is not None ):

                array = weightTable[ vertexIndex ]

                for ( j = 0, jl = array.length; j < jl; j ++ ):

                    weights.append( array[ j ].weight )
                    weightIndices.append( array[ j ].id )

                }

            }

            if weights.length > 4 ):

                if ! displayedWeightsWarning ):

                    console.warn( 'THREE.FBXLoader: Vertex has more than 4 skinning weights assigned to vertex. Deleting additional weights.' )
                    displayedWeightsWarning = true

                }

                WIndex = [ 0, 0, 0, 0 ]
                Weight = [ 0, 0, 0, 0 ]

                weights.forEach( def ( weight, weightIndex ):

                    currentWeight = weight
                    currentIndex = weightIndices[ weightIndex ]

                    Weight.forEach( def ( comparedWeight, comparedWeightIndex, comparedWeightArray ):

                        if currentWeight > comparedWeight ):

                            comparedWeightArray[ comparedWeightIndex ] = currentWeight
                            currentWeight = comparedWeight

                            tmp = WIndex[ comparedWeightIndex ]
                            WIndex[ comparedWeightIndex ] = currentIndex
                            currentIndex = tmp

                        }

                    } )

                } )

                weightIndices = WIndex
                weights = Weight

            }

            for ( i = weights.length; i < 4; ++ i ):

                weights[ i ] = 0
                weightIndices[ i ] = 0

            }

            vertex.skinWeights.fromArray( weights )
            vertex.skinIndices.fromArray( weightIndices )

        }

        if normalInfo ):

            vertex.normal.fromArray( getData( polygonVertexIndex, polygonIndex, vertexIndex, normalInfo ) )

        }

        if uvInfo ):

            vertex.uv.fromArray( getData( polygonVertexIndex, polygonIndex, vertexIndex, uvInfo ) )

        }

        if colorInfo ):

            vertex.color.fromArray( getData( polygonVertexIndex, polygonIndex, vertexIndex, colorInfo ) )

        }

        faceVertexBuffer.append( vertex )

        if endOfFace ):

            face = Face()
            face.genTrianglesFromVertices( faceVertexBuffer )

            if materialInfo is not None ):

                materials = getData( polygonVertexIndex, polygonIndex, vertexIndex, materialInfo )
                face.materialIndex = materials[ 0 ]

            else:

                # Seems like some models don't have materialInfo(subNodes.LayerElementMaterial).
                # Set 0 in such a case.
                face.materialIndex = 0

            }

            geometry.faces.append( face )
            faceVertexBuffer = []
            polygonIndex ++

            endOfFace = false

        }

    }

    """
     * @type {{vertexBuffer: number[], normalBuffer: number[], uvBuffer: number[], skinIndexBuffer: number[], skinWeightBuffer: number[], materialIndexBuffer: number[]}}
    """
    bufferInfo = geometry.flattenToBuffers()

    geo = THREE.BufferGeometry()
    geo.name = geometryNode.name
    geo.addAttribute( 'position', THREE.Float32BufferAttribute( bufferInfo.vertexBuffer, 3 ) )

    if bufferInfo.normalBuffer.length > 0 ):

        geo.addAttribute( 'normal', THREE.Float32BufferAttribute( bufferInfo.normalBuffer, 3 ) )

    }
    if bufferInfo.uvBuffer.length > 0 ):

        geo.addAttribute( 'uv', THREE.Float32BufferAttribute( bufferInfo.uvBuffer, 2 ) )

    }
    if subNodes.LayerElementColor ):

        geo.addAttribute( 'color', THREE.Float32BufferAttribute( bufferInfo.colorBuffer, 3 ) )

    }

    if deformer ):

        geo.addAttribute( 'skinIndex', THREE.Float32BufferAttribute( bufferInfo.skinIndexBuffer, 4 ) )

        geo.addAttribute( 'skinWeight', THREE.Float32BufferAttribute( bufferInfo.skinWeightBuffer, 4 ) )

        geo.FBX_Deformer = deformer

    }

    # Convert the material indices of each vertex into rendering groups on the geometry.

    materialIndexBuffer = bufferInfo.materialIndexBuffer
    prevMaterialIndex = materialIndexBuffer[ 0 ]
    startIndex = 0

    for ( i = 0; i < materialIndexBuffer.length; ++ i ):

        if materialIndexBuffer[ i ] !== prevMaterialIndex ):

            geo.addGroup( startIndex, i - startIndex, prevMaterialIndex )

            prevMaterialIndex = materialIndexBuffer[ i ]
            startIndex = i

        }

    }

    return geo

}

"""
 * Parses normal information for geometry.
 * @param {FBXGeometryNode} geometryNode
 * @returns {{dataSize: number, buffer: number[], indices: number[], mappingType: string, referenceType: string}}
"""
def getNormals( NormalNode ):

    mappingType = NormalNode.properties.MappingInformationType
    referenceType = NormalNode.properties.ReferenceInformationType
    buffer = parseFloatArray( NormalNode.subNodes.Normals.properties.a )
    indexBuffer = []
    if referenceType == 'IndexToDirect' ):

        if 'NormalIndex' in NormalNode.subNodes ):

            indexBuffer = parseIntArray( NormalNode.subNodes.NormalIndex.properties.a )

        elif 'NormalsIndex' in NormalNode.subNodes ):

            indexBuffer = parseIntArray( NormalNode.subNodes.NormalsIndex.properties.a )

        }

    }

    return {
        dataSize: 3,
        buffer: buffer,
        indices: indexBuffer,
        mappingType: mappingType,
        referenceType: referenceType
    }

}

"""
 * Parses UV information for geometry.
 * @param {FBXGeometryNode} geometryNode
 * @returns {{dataSize: number, buffer: number[], indices: number[], mappingType: string, referenceType: string}}
"""
def getUVs( UVNode ):

    mappingType = UVNode.properties.MappingInformationType
    referenceType = UVNode.properties.ReferenceInformationType
    buffer = parseFloatArray( UVNode.subNodes.UV.properties.a )
    indexBuffer = []
    if referenceType == 'IndexToDirect' ):

        indexBuffer = parseIntArray( UVNode.subNodes.UVIndex.properties.a )

    }

    return {
        dataSize: 2,
        buffer: buffer,
        indices: indexBuffer,
        mappingType: mappingType,
        referenceType: referenceType
    }

}

"""
 * Parses Vertex Color information for geometry.
 * @param {FBXGeometryNode} geometryNode
 * @returns {{dataSize: number, buffer: number[], indices: number[], mappingType: string, referenceType: string}}
"""
def getColors( ColorNode ):

    mappingType = ColorNode.properties.MappingInformationType
    referenceType = ColorNode.properties.ReferenceInformationType
    buffer = parseFloatArray( ColorNode.subNodes.Colors.properties.a )
    indexBuffer = []
    if referenceType == 'IndexToDirect' ):

        indexBuffer = parseFloatArray( ColorNode.subNodes.ColorIndex.properties.a )

    }

    return {
        dataSize: 4,
        buffer: buffer,
        indices: indexBuffer,
        mappingType: mappingType,
        referenceType: referenceType
    }

}

"""
 * Parses material application information for geometry.
 * @param {FBXGeometryNode}
 * @returns {{dataSize: number, buffer: number[], indices: number[], mappingType: string, referenceType: string}}
"""
def getMaterials( MaterialNode ):

    mappingType = MaterialNode.properties.MappingInformationType
    referenceType = MaterialNode.properties.ReferenceInformationType

    if mappingType == 'NoMappingInformation' ):

        return {
            dataSize: 1,
            buffer: [ 0 ],
            indices: [ 0 ],
            mappingType: 'AllSame',
            referenceType: referenceType
        }

    }

    materialIndexBuffer = parseIntArray( MaterialNode.subNodes.Materials.properties.a )

    # Since materials are stored as indices, there's a bit of a mismatch between FBX and what
    # we expect.  So we create an intermediate buffer that points to the index in the buffer,
    # for conforming with the other functions we've written for other data.
    materialIndices = []

    for ( materialIndexBufferIndex = 0, materialIndexBufferLength = materialIndexBuffer.length; materialIndexBufferIndex < materialIndexBufferLength; ++ materialIndexBufferIndex ):

        materialIndices.append( materialIndexBufferIndex )

    }

    return {
        dataSize: 1,
        buffer: materialIndexBuffer,
        indices: materialIndices,
        mappingType: mappingType,
        referenceType: referenceType
    }

}

"""
 * def uses the infoObject and given indices to return value array of object.
 * @param {number} polygonVertexIndex - Index of vertex in draw order (which index of the index buffer refers to this vertex).
 * @param {number} polygonIndex - Index of polygon in geometry.
 * @param {number} vertexIndex - Index of vertex inside vertex buffer (used because some data refers to old index buffer that we don't use anymore).
 * @param {{datasize: number, buffer: number[], indices: number[], mappingType: string, referenceType: string}} infoObject - Object containing data and how to access data.
 * @returns {number[]}
"""

dataArray = []

GetData = {

    ByPolygonVertex: {

        """
         * def uses the infoObject and given indices to return value array of object.
         * @param {number} polygonVertexIndex - Index of vertex in draw order (which index of the index buffer refers to this vertex).
         * @param {number} polygonIndex - Index of polygon in geometry.
         * @param {number} vertexIndex - Index of vertex inside vertex buffer (used because some data refers to old index buffer that we don't use anymore).
         * @param {{datasize: number, buffer: number[], indices: number[], mappingType: string, referenceType: string}} infoObject - Object containing data and how to access data.
         * @returns {number[]}
        """
        Direct(self, polygonVertexIndex, polygonIndex, vertexIndex, infoObject ):

            from = ( polygonVertexIndex * infoObject.dataSize )
            to = ( polygonVertexIndex * infoObject.dataSize ) + infoObject.dataSize

            # return infoObject.buffer.slice( from, to )
            return slice( dataArray, infoObject.buffer, from, to )

        },

        """
         * def uses the infoObject and given indices to return value array of object.
         * @param {number} polygonVertexIndex - Index of vertex in draw order (which index of the index buffer refers to this vertex).
         * @param {number} polygonIndex - Index of polygon in geometry.
         * @param {number} vertexIndex - Index of vertex inside vertex buffer (used because some data refers to old index buffer that we don't use anymore).
         * @param {{datasize: number, buffer: number[], indices: number[], mappingType: string, referenceType: string}} infoObject - Object containing data and how to access data.
         * @returns {number[]}
        """
        IndexToDirect(self, polygonVertexIndex, polygonIndex, vertexIndex, infoObject ):

            index = infoObject.indices[ polygonVertexIndex ]
            from = ( index * infoObject.dataSize )
            to = ( index * infoObject.dataSize ) + infoObject.dataSize

            # return infoObject.buffer.slice( from, to )
            return slice( dataArray, infoObject.buffer, from, to )

        }

    },

    ByPolygon: {

        """
         * def uses the infoObject and given indices to return value array of object.
         * @param {number} polygonVertexIndex - Index of vertex in draw order (which index of the index buffer refers to this vertex).
         * @param {number} polygonIndex - Index of polygon in geometry.
         * @param {number} vertexIndex - Index of vertex inside vertex buffer (used because some data refers to old index buffer that we don't use anymore).
         * @param {{datasize: number, buffer: number[], indices: number[], mappingType: string, referenceType: string}} infoObject - Object containing data and how to access data.
         * @returns {number[]}
        """
        Direct(self, polygonVertexIndex, polygonIndex, vertexIndex, infoObject ):

            from = polygonIndex * infoObject.dataSize
            to = polygonIndex * infoObject.dataSize + infoObject.dataSize

            # return infoObject.buffer.slice( from, to )
            return slice( dataArray, infoObject.buffer, from, to )

        },

        """
         * def uses the infoObject and given indices to return value array of object.
         * @param {number} polygonVertexIndex - Index of vertex in draw order (which index of the index buffer refers to this vertex).
         * @param {number} polygonIndex - Index of polygon in geometry.
         * @param {number} vertexIndex - Index of vertex inside vertex buffer (used because some data refers to old index buffer that we don't use anymore).
         * @param {{datasize: number, buffer: number[], indices: number[], mappingType: string, referenceType: string}} infoObject - Object containing data and how to access data.
         * @returns {number[]}
        """
        IndexToDirect(self, polygonVertexIndex, polygonIndex, vertexIndex, infoObject ):

            index = infoObject.indices[ polygonIndex ]
            from = index * infoObject.dataSize
            to = index * infoObject.dataSize + infoObject.dataSize

            # return infoObject.buffer.slice( from, to )
            return slice( dataArray, infoObject.buffer, from, to )

        }

    },

    ByVertice: {

        Direct(self, polygonVertexIndex, polygonIndex, vertexIndex, infoObject ):

            from = ( vertexIndex * infoObject.dataSize )
            to = ( vertexIndex * infoObject.dataSize ) + infoObject.dataSize

            # return infoObject.buffer.slice( from, to )
            return slice( dataArray, infoObject.buffer, from, to )

        }

    },

    AllSame: {

        """
         * def uses the infoObject and given indices to return value array of object.
         * @param {number} polygonVertexIndex - Index of vertex in draw order (which index of the index buffer refers to this vertex).
         * @param {number} polygonIndex - Index of polygon in geometry.
         * @param {number} vertexIndex - Index of vertex inside vertex buffer (used because some data refers to old index buffer that we don't use anymore).
         * @param {{datasize: number, buffer: number[], indices: number[], mappingType: string, referenceType: string}} infoObject - Object containing data and how to access data.
         * @returns {number[]}
        """
        IndexToDirect(self, polygonVertexIndex, polygonIndex, vertexIndex, infoObject ):

            from = infoObject.indices[ 0 ] * infoObject.dataSize
            to = infoObject.indices[ 0 ] * infoObject.dataSize + infoObject.dataSize

            # return infoObject.buffer.slice( from, to )
            return slice( dataArray, infoObject.buffer, from, to )

        }

    }

}

def getData( polygonVertexIndex, polygonIndex, vertexIndex, infoObject ):

    return GetData[ infoObject.mappingType ][ infoObject.referenceType ]( polygonVertexIndex, polygonIndex, vertexIndex, infoObject )

}

"""
 * Specialty def for parsing NurbsCurve based Geometry Nodes.
 * @param {FBXGeometryNode} geometryNode
 * @param {{parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}} relationships
 * @returns {THREE.BufferGeometry}
"""
def parseNurbsGeometry( geometryNode ):

    if THREE.NURBSCurve == undefined ):

        console.error( 'THREE.FBXLoader: The loader relies on THREE.NURBSCurve for any nurbs present in the model. Nurbs will show up as empty geometry.' )
        return THREE.BufferGeometry()

    }

    order = parseInt( geometryNode.properties.Order )

    if isNaN( order ) ):

        console.error( 'THREE.FBXLoader: Invalid Order %s given for geometry ID: %s', geometryNode.properties.Order, geometryNode.id )
        return THREE.BufferGeometry()

    }

    degree = order - 1

    knots = parseFloatArray( geometryNode.subNodes.KnotVector.properties.a )
    controlPoints = []
    pointsValues = parseFloatArray( geometryNode.subNodes.Points.properties.a )

    for ( i = 0, l = pointsValues.length; i < l; i += 4 ):

        controlPoints.append( THREE.Vector4().fromArray( pointsValues, i ) )

    }

    startKnot, endKnot

    if geometryNode.properties.Form == 'Closed' ):

        controlPoints.append( controlPoints[ 0 ] )

    elif geometryNode.properties.Form == 'Periodic' ):

        startKnot = degree
        endKnot = knots.length - 1 - startKnot

        for ( i = 0; i < degree; ++ i ):

            controlPoints.append( controlPoints[ i ] )

        }

    }

    curve = THREE.NURBSCurve( degree, knots, controlPoints, startKnot, endKnot )
    vertices = curve.getPoints( controlPoints.length * 7 )

    positions = Float32Array( vertices.length * 3 )

    for ( i = 0, l = vertices.length; i < l; ++ i ):

        vertices[ i ].toArray( positions, i * 3 )

    }

    geometry = THREE.BufferGeometry()
    geometry.addAttribute( 'position', THREE.BufferAttribute( positions, 3 ) )

    return geometry

}

"""
 * Finally generates Scene graph and Scene graph Objects.
 * @param {{Objects: {subNodes: {Model: Object.<number, FBXModelNode>}}}} FBXTree
 * @param {Map<number, {parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}>} connections
 * @param {Map<number, {map: Map<number, {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}>, array: {FBX_ID: number, indices: number[], weights: number[], transform: number[], transformLink: number[], linkMode: string}[], skeleton: THREE.Skeleton|null}>} deformers
 * @param {Map<number, THREE.BufferGeometry>} geometryMap
 * @param {Map<number, THREE.Material>} materialMap
 * @returns {THREE.Group}
"""
def parseScene( FBXTree, connections, deformers, geometryMap, materialMap ):

    sceneGraph = THREE.Group()

    ModelNode = FBXTree.Objects.subNodes.Model

    """
     * @type {Array.<THREE.Object3D>}
    """
    modelArray = []

    """
     * @type {Map.<number, THREE.Object3D>}
    """
    modelMap = Map()

    for ( nodeID in ModelNode ):

        id = parseInt( nodeID )
        node = ModelNode[ nodeID ]
        conns = connections.get( id )
        model = null

        for ( i = 0; i < conns.parents.length; ++ i ):

            for ( FBX_ID in deformers ):

                deformer = deformers[ FBX_ID ]
                subDeformers = deformer.map
                subDeformer = subDeformers[ conns.parents[ i ].ID ]

                if subDeformer ):

                    model2 = model
                    model = THREE.Bone()
                    deformer.bones[ subDeformer.index ] = model

                    # seems like we need this not to make non-connected bone, maybe?
                    # TODO: confirm
                    if model2 !== null ) model.add( model2 )

                }

            }

        }

        if ! model ):

            switch ( node.attrType ):

                case 'Mesh':
                    """
                     * @type {?THREE.BufferGeometry}
                    """
                    geometry = null

                    """
                     * @type {THREE.MultiMaterial|THREE.Material}
                    """
                    material = null

                    """
                     * @type {Array.<THREE.Material>}
                    """
                    materials = []

                    for ( childrenIndex = 0, childrenLength = conns.children.length; childrenIndex < childrenLength; ++ childrenIndex ):

                        child = conns.children[ childrenIndex ]

                        if geometryMap.has( child.ID ) ):

                            geometry = geometryMap.get( child.ID )

                        }

                        if materialMap.has( child.ID ) ):

                            materials.append( materialMap.get( child.ID ) )

                        }

                    }
                    if materials.length > 1 ):

                        material = materials

                    elif materials.length > 0 ):

                        material = materials[ 0 ]

                    else:

                        material = THREE.MeshBasicMaterial( { color: 0x3300ff } )
                        materials.append( material )

                    }
                    if 'color' in geometry.attributes ):

                        for ( materialIndex = 0, numMaterials = materials.length; materialIndex < numMaterials; ++materialIndex ):

                            materials[ materialIndex ].vertexColors = THREE.VertexColors

                        }

                    }
                    if geometry.FBX_Deformer ):

                        for ( materialsIndex = 0, materialsLength = materials.length; materialsIndex < materialsLength; ++ materialsIndex ):

                            materials[ materialsIndex ].skinning = true

                        }
                        model = THREE.SkinnedMesh( geometry, material )

                    else:

                        model = THREE.Mesh( geometry, material )

                    }
                    break

                case 'NurbsCurve':
                    geometry = null

                    for ( childrenIndex = 0, childrenLength = conns.children.length; childrenIndex < childrenLength; ++ childrenIndex ):

                        child = conns.children[ childrenIndex ]

                        if geometryMap.has( child.ID ) ):

                            geometry = geometryMap.get( child.ID )

                        }

                    }

                    # FBX does not list materials for Nurbs lines, so we'll just put our own in here.
                    material = THREE.LineBasicMaterial( { color: 0x3300ff, linewidth: 5 } )
                    model = THREE.Line( geometry, material )
                    break

                default:
                    model = THREE.Object3D()
                    break

            }

        }

        model.name = node.attrName.replace( /:/, '' ).replace( /_/, '' ).replace( /-/, '' )
        model.FBX_ID = id

        modelArray.append( model )
        modelMap.set( id, model )

    }

    for ( modelArrayIndex = 0, modelArrayLength = modelArray.length; modelArrayIndex < modelArrayLength; ++ modelArrayIndex ):

        model = modelArray[ modelArrayIndex ]

        node = ModelNode[ model.FBX_ID ]

        if 'Lcl_Translation' in node.properties ):

            model.position.fromArray( parseFloatArray( node.properties.Lcl_Translation.value ) )

        }

        if 'Lcl_Rotation' in node.properties ):

            rotation = parseFloatArray( node.properties.Lcl_Rotation.value ).map( degreeToRadian )
            rotation.append( 'ZYX' )
            model.rotation.fromArray( rotation )

        }

        if 'Lcl_Scaling' in node.properties ):

            model.scale.fromArray( parseFloatArray( node.properties.Lcl_Scaling.value ) )

        }

        if 'PreRotation' in node.properties ):

            preRotations = THREE.Euler().setFromVector3( parseVector3( node.properties.PreRotation ).multiplyScalar( DEG2RAD ), 'ZYX' )
            preRotations = THREE.Quaternion().setFromEuler( preRotations )
            currentRotation = THREE.Quaternion().setFromEuler( model.rotation )
            preRotations.multiply( currentRotation )
            model.rotation.setFromQuaternion( preRotations, 'ZYX' )

        }

        conns = connections.get( model.FBX_ID )
        for ( parentIndex = 0; parentIndex < conns.parents.length; parentIndex ++ ):

            pIndex = findIndex( modelArray, def ( mod ):

                return mod.FBX_ID == conns.parents[ parentIndex ].ID

            } )
            if pIndex > - 1 ):

                modelArray[ pIndex ].add( model )
                break

            }

        }
        if model.parent is None ):

            sceneGraph.add( model )

        }

    }


    # Now with the bones created, we can update the skeletons and bind them to the skinned meshes.
    sceneGraph.updateMatrixWorld( true )

    # Put skeleton into bind pose.
    BindPoseNode = FBXTree.Objects.subNodes.Pose
    for ( nodeID in BindPoseNode ):

        if BindPoseNode[ nodeID ].attrType == 'BindPose' ):

            BindPoseNode = BindPoseNode[ nodeID ]
            break

        }

    }
    if BindPoseNode ):

        PoseNode = BindPoseNode.subNodes.PoseNode
        worldMatrices = Map()

        for ( PoseNodeIndex = 0, PoseNodeLength = PoseNode.length; PoseNodeIndex < PoseNodeLength; ++ PoseNodeIndex ):

            node = PoseNode[ PoseNodeIndex ]

            rawMatWrd = parseMatrixArray( node.subNodes.Matrix.properties.a )

            worldMatrices.set( parseInt( node.id ), rawMatWrd )

        }

    }

    for ( FBX_ID in deformers ):

        deformer = deformers[ FBX_ID ]
        subDeformers = deformer.map

        for ( key in subDeformers ):

            subDeformer = subDeformers[ key ]
            subDeformerIndex = subDeformer.index

            """
             * @type {THREE.Bone}
            """
            bone = deformer.bones[ subDeformerIndex ]
            if ! worldMatrices.has( bone.FBX_ID ) ):

                break

            }
            mat = worldMatrices.get( bone.FBX_ID )
            bone.matrixWorld.copy( mat )

        }

        # Now that skeleton is in bind pose, bind to model.
        deformer.skeleton = THREE.Skeleton( deformer.bones )

        conns = connections.get( deformer.FBX_ID )
        parents = conns.parents

        for ( parentsIndex = 0, parentsLength = parents.length; parentsIndex < parentsLength; ++ parentsIndex ):

            parent = parents[ parentsIndex ]

            if geometryMap.has( parent.ID ) ):

                geoID = parent.ID
                geoConns = connections.get( geoID )

                for ( i = 0; i < geoConns.parents.length; ++ i ):

                    if modelMap.has( geoConns.parents[ i ].ID ) ):

                        model = modelMap.get( geoConns.parents[ i ].ID )
                        #ASSERT model typeof SkinnedMesh
                        model.bind( deformer.skeleton, model.matrixWorld )
                        break

                    }

                }

            }

        }

    }

    #Skeleton is now bound, return objects to starting
    #world positions.
    sceneGraph.updateMatrixWorld( true )

    # Silly hack with the animation parsing.  We're gonna pretend the scene graph has a skeleton
    # to attach animations to, since FBXs treat animations as animations for the entire scene,
    # not just for individual objects.
    sceneGraph.skeleton = {
        bones: modelArray
    }

    animations = parseAnimations( FBXTree, connections, sceneGraph )

    addAnimations( sceneGraph, animations )

    return sceneGraph

}

"""
 * Parses animation information from FBXTree and generates an AnimationInfoObject.
 * @param {{Objects: {subNodes: {AnimationCurveNode: any, AnimationCurve: any, AnimationLayer: any, AnimationStack: any}}}} FBXTree
 * @param {Map<number, {parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}>} connections
"""
def parseAnimations( FBXTree, connections, sceneGraph ):

    rawNodes = FBXTree.Objects.subNodes.AnimationCurveNode
    rawCurves = FBXTree.Objects.subNodes.AnimationCurve
    rawLayers = FBXTree.Objects.subNodes.AnimationLayer
    rawStacks = FBXTree.Objects.subNodes.AnimationStack

    """
     * @type {{
             curves: Map<number, {
             T: {
                id: number
                attr: string
                internalID: number
                attrX: boolean
                attrY: boolean
                attrZ: boolean
                containerBoneID: number
                containerID: number
                curves: {
                    x: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    y: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    z: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                }
            },
             R: {
                id: number
                attr: string
                internalID: number
                attrX: boolean
                attrY: boolean
                attrZ: boolean
                containerBoneID: number
                containerID: number
                curves: {
                    x: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    y: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    z: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                }
            },
             S: {
                id: number
                attr: string
                internalID: number
                attrX: boolean
                attrY: boolean
                attrZ: boolean
                containerBoneID: number
                containerID: number
                curves: {
                    x: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    y: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    z: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                }
            }
         }>,
         layers: Map<number, {
            T: {
                id: number
                attr: string
                internalID: number
                attrX: boolean
                attrY: boolean
                attrZ: boolean
                containerBoneID: number
                containerID: number
                curves: {
                    x: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    y: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    z: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                },
            },
            R: {
                id: number
                attr: string
                internalID: number
                attrX: boolean
                attrY: boolean
                attrZ: boolean
                containerBoneID: number
                containerID: number
                curves: {
                    x: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    y: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    z: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                },
            },
            S: {
                id: number
                attr: string
                internalID: number
                attrX: boolean
                attrY: boolean
                attrZ: boolean
                containerBoneID: number
                containerID: number
                curves: {
                    x: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    y: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    z: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                },
            }
            }[]>,
         stacks: Map<number, {
             name: string,
             layers: {
                T: {
                    id: number
                    attr: string
                    internalID: number
                    attrX: boolean
                    attrY: boolean
                    attrZ: boolean
                    containerBoneID: number
                    containerID: number
                    curves: {
                        x: {
                            version: any
                            id: number
                            internalID: number
                            times: number[]
                            values: number[]
                            attrFlag: number[]
                            attrData: number[]
                        }
                        y: {
                            version: any
                            id: number
                            internalID: number
                            times: number[]
                            values: number[]
                            attrFlag: number[]
                            attrData: number[]
                        }
                        z: {
                            version: any
                            id: number
                            internalID: number
                            times: number[]
                            values: number[]
                            attrFlag: number[]
                            attrData: number[]
                        }
                    }
                }
                R: {
                    id: number
                    attr: string
                    internalID: number
                    attrX: boolean
                    attrY: boolean
                    attrZ: boolean
                    containerBoneID: number
                    containerID: number
                    curves: {
                        x: {
                            version: any
                            id: number
                            internalID: number
                            times: number[]
                            values: number[]
                            attrFlag: number[]
                            attrData: number[]
                        }
                        y: {
                            version: any
                            id: number
                            internalID: number
                            times: number[]
                            values: number[]
                            attrFlag: number[]
                            attrData: number[]
                        }
                        z: {
                            version: any
                            id: number
                            internalID: number
                            times: number[]
                            values: number[]
                            attrFlag: number[]
                            attrData: number[]
                        }
                    }
                }
                S: {
                    id: number
                    attr: string
                    internalID: number
                    attrX: boolean
                    attrY: boolean
                    attrZ: boolean
                    containerBoneID: number
                    containerID: number
                    curves: {
                        x: {
                            version: any
                            id: number
                            internalID: number
                            times: number[]
                            values: number[]
                            attrFlag: number[]
                            attrData: number[]
                        }
                        y: {
                            version: any
                            id: number
                            internalID: number
                            times: number[]
                            values: number[]
                            attrFlag: number[]
                            attrData: number[]
                        }
                        z: {
                            version: any
                            id: number
                            internalID: number
                            times: number[]
                            values: number[]
                            attrFlag: number[]
                            attrData: number[]
                        }
                    }
                }
            }[][],
         length: number,
         frames: number }>,
         length: number,
         fps: number,
         frames: number
     }}
    """
    returnObject = {
        curves: Map(),
        layers: {},
        stacks: {},
        length: 0,
        fps: 30,
        frames: 0
    }

    """
     * @type {Array.<{
            id: number
            attr: string
            internalID: number
            attrX: boolean
            attrY: boolean
            attrZ: boolean
            containerBoneID: number
            containerID: number
        }>}
    """
    animationCurveNodes = []
    for ( nodeID in rawNodes ):

        if nodeID.match( /\d+/ ) ):

            animationNode = parseAnimationNode( FBXTree, rawNodes[ nodeID ], connections, sceneGraph )
            animationCurveNodes.append( animationNode )

        }

    }

    """
     * @type {Map.<number, {
            id: number,
            attr: string,
            internalID: number,
            attrX: boolean,
            attrY: boolean,
            attrZ: boolean,
            containerBoneID: number,
            containerID: number,
            curves: {
                x: {
                    version: any,
                    id: number,
                    internalID: number,
                    times: number[],
                    values: number[],
                    attrFlag: number[],
                    attrData: number[],
                },
                y: {
                    version: any,
                    id: number,
                    internalID: number,
                    times: number[],
                    values: number[],
                    attrFlag: number[],
                    attrData: number[],
                },
                z: {
                    version: any,
                    id: number,
                    internalID: number,
                    times: number[],
                    values: number[],
                    attrFlag: number[],
                    attrData: number[],
                }
            }
        }>}
    """
    tmpMap = Map()
    for ( animationCurveNodeIndex = 0; animationCurveNodeIndex < animationCurveNodes.length; ++ animationCurveNodeIndex ):

        if animationCurveNodes[ animationCurveNodeIndex ] is None ):

            continue

        }
        tmpMap.set( animationCurveNodes[ animationCurveNodeIndex ].id, animationCurveNodes[ animationCurveNodeIndex ] )

    }


    """
     * @type {{
            version: any,
            id: number,
            internalID: number,
            times: number[],
            values: number[],
            attrFlag: number[],
            attrData: number[],
        }[]}
    """
    animationCurves = []
    for ( nodeID in rawCurves ):

        if nodeID.match( /\d+/ ) ):

            animationCurve = parseAnimationCurve( rawCurves[ nodeID ] )

            # seems like this check would be necessary?
            if ! connections.has( animationCurve.id ) ) continue

            animationCurves.append( animationCurve )

            firstParentConn = connections.get( animationCurve.id ).parents[ 0 ]
            firstParentID = firstParentConn.ID
            firstParentRelationship = firstParentConn.relationship
            axis = ''

            if firstParentRelationship.match( /X/ ) ):

                axis = 'x'

            elif firstParentRelationship.match( /Y/ ) ):

                axis = 'y'

            elif firstParentRelationship.match( /Z/ ) ):

                axis = 'z'

            else:

                continue

            }

            tmpMap.get( firstParentID ).curves[ axis ] = animationCurve

        }

    }

    tmpMap.forEach( def ( curveNode ):

        id = curveNode.containerBoneID
        if ! returnObject.curves.has( id ) ):

            returnObject.curves.set( id, { T: null, R: null, S: null } )

        }
        returnObject.curves.get( id )[ curveNode.attr ] = curveNode
        if curveNode.attr == 'R' ):

            curves = curveNode.curves

            # Seems like some FBX files have AnimationCurveNode
            # which doesn't have any connected AnimationCurve.
            # Setting animation parameter for them here.

            if curves.x is None ):

                curves.x = {
                    version: null,
                    times: [ 0.0 ],
                    values: [ 0.0 ]
                }

            }

            if curves.y is None ):

                curves.y = {
                    version: null,
                    times: [ 0.0 ],
                    values: [ 0.0 ]
                }

            }

            if curves.z is None ):

                curves.z = {
                    version: null,
                    times: [ 0.0 ],
                    values: [ 0.0 ]
                }

            }

            curves.x.values = curves.x.values.map( degreeToRadian )
            curves.y.values = curves.y.values.map( degreeToRadian )
            curves.z.values = curves.z.values.map( degreeToRadian )

            if curveNode.preRotations !== null ):

                preRotations = THREE.Euler().setFromVector3( curveNode.preRotations, 'ZYX' )
                preRotations = THREE.Quaternion().setFromEuler( preRotations )
                frameRotation = THREE.Euler()
                frameRotationQuaternion = THREE.Quaternion()
                for ( frame = 0; frame < curves.x.times.length; ++ frame ):

                    frameRotation.set( curves.x.values[ frame ], curves.y.values[ frame ], curves.z.values[ frame ], 'ZYX' )
                    frameRotationQuaternion.setFromEuler( frameRotation ).premultiply( preRotations )
                    frameRotation.setFromQuaternion( frameRotationQuaternion, 'ZYX' )
                    curves.x.values[ frame ] = frameRotation.x
                    curves.y.values[ frame ] = frameRotation.y
                    curves.z.values[ frame ] = frameRotation.z

                }

            }

        }

    } )

    for ( nodeID in rawLayers ):

        """
         * @type {{
            T: {
                id: number
                attr: string
                internalID: number
                attrX: boolean
                attrY: boolean
                attrZ: boolean
                containerBoneID: number
                containerID: number
                curves: {
                    x: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    y: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    z: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                },
            },
            R: {
                id: number
                attr: string
                internalID: number
                attrX: boolean
                attrY: boolean
                attrZ: boolean
                containerBoneID: number
                containerID: number
                curves: {
                    x: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    y: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    z: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                },
            },
            S: {
                id: number
                attr: string
                internalID: number
                attrX: boolean
                attrY: boolean
                attrZ: boolean
                containerBoneID: number
                containerID: number
                curves: {
                    x: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    y: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    z: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                },
            }
            }[]}
        """
        layer = []
        children = connections.get( parseInt( nodeID ) ).children

        for ( childIndex = 0; childIndex < children.length; childIndex ++ ):

            # Skip lockInfluenceWeights
            if tmpMap.has( children[ childIndex ].ID ) ):

                curveNode = tmpMap.get( children[ childIndex ].ID )
                boneID = curveNode.containerBoneID
                if layer[ boneID ] == undefined ):

                    layer[ boneID ] = {
                        T: null,
                        R: null,
                        S: null
                    }

                }

                layer[ boneID ][ curveNode.attr ] = curveNode

            }

        }

        returnObject.layers[ nodeID ] = layer

    }

    for ( nodeID in rawStacks ):

        layers = []
        children = connections.get( parseInt( nodeID ) ).children
        timestamps = { max: 0, min: Number.MAX_VALUE }

        for ( childIndex = 0; childIndex < children.length; ++ childIndex ):

            currentLayer = returnObject.layers[ children[ childIndex ].ID ]

            if currentLayer is not None ):

                layers.append( currentLayer )

                for ( currentLayerIndex = 0, currentLayerLength = currentLayer.length; currentLayerIndex < currentLayerLength; ++ currentLayerIndex ):

                    layer = currentLayer[ currentLayerIndex ]

                    if layer ):

                        getCurveNodeMaxMinTimeStamps( layer, timestamps )

                    }

                }

            }

        }

        # Do we have an animation clip with actual length?
        if timestamps.max > timestamps.min ):

            returnObject.stacks[ nodeID ] = {
                name: rawStacks[ nodeID ].attrName,
                layers: layers,
                length: timestamps.max - timestamps.min,
                frames: ( timestamps.max - timestamps.min ) * 30
            }

        }

    }

    return returnObject

}

"""
 * @param {Object} FBXTree
 * @param {{id: number, attrName: string, properties: Object<string, any>}} animationCurveNode
 * @param {Map<number, {parents: {ID: number, relationship: string}[], children: {ID: number, relationship: string}[]}>} connections
 * @param {{skeleton: {bones: {FBX_ID: number}[]}}} sceneGraph
"""
def parseAnimationNode( FBXTree, animationCurveNode, connections, sceneGraph ):

    rawModels = FBXTree.Objects.subNodes.Model

    returnObject = {
        """
         * @type {number}
        """
        id: animationCurveNode.id,

        """
         * @type {string}
        """
        attr: animationCurveNode.attrName,

        """
         * @type {number}
        """
        internalID: animationCurveNode.id,

        """
         * @type {boolean}
        """
        attrX: false,

        """
         * @type {boolean}
        """
        attrY: false,

        """
         * @type {boolean}
        """
        attrZ: false,

        """
         * @type {number}
        """
        containerBoneID: - 1,

        """
         * @type {number}
        """
        containerID: - 1,

        curves: {
            x: null,
            y: null,
            z: null
        },

        """
         * @type {number[]}
        """
        preRotations: null
    }

    if returnObject.attr.match( /S|R|T/ ) ):

        for ( attributeKey in animationCurveNode.properties ):

            if attributeKey.match( /X/ ) ):

                returnObject.attrX = true

            }
            if attributeKey.match( /Y/ ) ):

                returnObject.attrY = true

            }
            if attributeKey.match( /Z/ ) ):

                returnObject.attrZ = true

            }

        }

    else:

        return null

    }

    conns = connections.get( returnObject.id )
    containerIndices = conns.parents

    for ( containerIndicesIndex = containerIndices.length - 1; containerIndicesIndex >= 0; -- containerIndicesIndex ):

        boneID = findIndex( sceneGraph.skeleton.bones, def ( bone ):

            return bone.FBX_ID == containerIndices[ containerIndicesIndex ].ID

        } )
        if boneID > - 1 ):

            returnObject.containerBoneID = boneID
            returnObject.containerID = containerIndices[ containerIndicesIndex ].ID
            model = rawModels[ returnObject.containerID.toString() ]
            if 'PreRotation' in model.properties ):

                returnObject.preRotations = parseVector3( model.properties.PreRotation ).multiplyScalar( Math.PI / 180 )

            }
            break

        }

    }

    return returnObject

}

"""
 * @param {{id: number, subNodes: {KeyTime: {properties: {a: string}}, KeyValueFloat: {properties: {a: string}}, KeyAttrFlags: {properties: {a: string}}, KeyAttrDataFloat: {properties: {a: string}}}}} animationCurve
"""
def parseAnimationCurve( animationCurve ):

    return {
        version: null,
        id: animationCurve.id,
        internalID: animationCurve.id,
        times: parseFloatArray( animationCurve.subNodes.KeyTime.properties.a ).map( convertFBXTimeToSeconds ),
        values: parseFloatArray( animationCurve.subNodes.KeyValueFloat.properties.a ),

        attrFlag: parseIntArray( animationCurve.subNodes.KeyAttrFlags.properties.a ),
        attrData: parseFloatArray( animationCurve.subNodes.KeyAttrDataFloat.properties.a )
    }

}

"""
 * Sets the maxTimeStamp and minTimeStamp variables if it has timeStamps that are either larger or smaller
 * than the max or min respectively.
 * @param {{
            T: {
                    id: number,
                    attr: string,
                    internalID: number,
                    attrX: boolean,
                    attrY: boolean,
                    attrZ: boolean,
                    containerBoneID: number,
                    containerID: number,
                    curves: {
                            x: {
                                    version: any,
                                    id: number,
                                    internalID: number,
                                    times: number[],
                                    values: number[],
                                    attrFlag: number[],
                                    attrData: number[],
                            },
                            y: {
                                    version: any,
                                    id: number,
                                    internalID: number,
                                    times: number[],
                                    values: number[],
                                    attrFlag: number[],
                                    attrData: number[],
                            },
                            z: {
                                    version: any,
                                    id: number,
                                    internalID: number,
                                    times: number[],
                                    values: number[],
                                    attrFlag: number[],
                                    attrData: number[],
                            },
                    },
            },
            R: {
                    id: number,
                    attr: string,
                    internalID: number,
                    attrX: boolean,
                    attrY: boolean,
                    attrZ: boolean,
                    containerBoneID: number,
                    containerID: number,
                    curves: {
                            x: {
                                    version: any,
                                    id: number,
                                    internalID: number,
                                    times: number[],
                                    values: number[],
                                    attrFlag: number[],
                                    attrData: number[],
                            },
                            y: {
                                    version: any,
                                    id: number,
                                    internalID: number,
                                    times: number[],
                                    values: number[],
                                    attrFlag: number[],
                                    attrData: number[],
                            },
                            z: {
                                    version: any,
                                    id: number,
                                    internalID: number,
                                    times: number[],
                                    values: number[],
                                    attrFlag: number[],
                                    attrData: number[],
                            },
                    },
            },
            S: {
                    id: number,
                    attr: string,
                    internalID: number,
                    attrX: boolean,
                    attrY: boolean,
                    attrZ: boolean,
                    containerBoneID: number,
                    containerID: number,
                    curves: {
                            x: {
                                    version: any,
                                    id: number,
                                    internalID: number,
                                    times: number[],
                                    values: number[],
                                    attrFlag: number[],
                                    attrData: number[],
                            },
                            y: {
                                    version: any,
                                    id: number,
                                    internalID: number,
                                    times: number[],
                                    values: number[],
                                    attrFlag: number[],
                                    attrData: number[],
                            },
                            z: {
                                    version: any,
                                    id: number,
                                    internalID: number,
                                    times: number[],
                                    values: number[],
                                    attrFlag: number[],
                                    attrData: number[],
                            },
                    },
            },
    }} layer
"""
def getCurveNodeMaxMinTimeStamps( layer, timestamps ):

    if layer.R ):

        getCurveMaxMinTimeStamp( layer.R.curves, timestamps )

    }
    if layer.S ):

        getCurveMaxMinTimeStamp( layer.S.curves, timestamps )

    }
    if layer.T ):

        getCurveMaxMinTimeStamp( layer.T.curves, timestamps )

    }

}

"""
 * Sets the maxTimeStamp and minTimeStamp if one of the curve's time stamps
 * exceeds the maximum or minimum.
 * @param {{
            x: {
                    version: any,
                    id: number,
                    internalID: number,
                    times: number[],
                    values: number[],
                    attrFlag: number[],
                    attrData: number[],
            },
            y: {
                    version: any,
                    id: number,
                    internalID: number,
                    times: number[],
                    values: number[],
                    attrFlag: number[],
                    attrData: number[],
            },
            z: {
                    version: any,
                    id: number,
                    internalID: number,
                    times: number[],
                    values: number[],
                    attrFlag: number[],
                    attrData: number[],
            }
    }} curve
"""
def getCurveMaxMinTimeStamp( curve, timestamps ):

    if curve.x ):

        getCurveAxisMaxMinTimeStamps( curve.x, timestamps )

    }
    if curve.y ):

        getCurveAxisMaxMinTimeStamps( curve.y, timestamps )

    }
    if curve.z ):

        getCurveAxisMaxMinTimeStamps( curve.z, timestamps )

    }

}

"""
 * Sets the maxTimeStamp and minTimeStamp if one of its timestamps exceeds the maximum or minimum.
 * @param {{times: number[]}} axis
"""
def getCurveAxisMaxMinTimeStamps( axis, timestamps ):

    timestamps.max = axis.times[ axis.times.length - 1 ] > timestamps.max ? axis.times[ axis.times.length - 1 ] : timestamps.max
    timestamps.min = axis.times[ 0 ] < timestamps.min ? axis.times[ 0 ] : timestamps.min

}

"""
 * @param {{
    curves: Map<number, {
        T: {
            id: number
            attr: string
            internalID: number
            attrX: boolean
            attrY: boolean
            attrZ: boolean
            containerBoneID: number
            containerID: number
            curves: {
                x: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
                y: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
                z: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
            }
        }
        R: {
            id: number
            attr: string
            internalID: number
            attrX: boolean
            attrY: boolean
            attrZ: boolean
            containerBoneID: number
            containerID: number
            curves: {
                x: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
                y: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
                z: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
            }
        }
        S: {
            id: number
            attr: string
            internalID: number
            attrX: boolean
            attrY: boolean
            attrZ: boolean
            containerBoneID: number
            containerID: number
            curves: {
                x: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
                y: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
                z: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
            }
        }
    }>
    layers: Map<number, {
        T: {
            id: number
            attr: string
            internalID: number
            attrX: boolean
            attrY: boolean
            attrZ: boolean
            containerBoneID: number
            containerID: number
            curves: {
                x: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
                y: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
                z: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
            }
        }
        R: {
            id: number
            attr: string
            internalID: number
            attrX: boolean
            attrY: boolean
            attrZ: boolean
            containerBoneID: number
            containerID: number
            curves: {
                x: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
                y: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
                z: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
            }
        }
        S: {
            id: number
            attr: string
            internalID: number
            attrX: boolean
            attrY: boolean
            attrZ: boolean
            containerBoneID: number
            containerID: number
            curves: {
                x: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
                y: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
                z: {
                    version: any
                    id: number
                    internalID: number
                    times: number[]
                    values: number[]
                    attrFlag: number[]
                    attrData: number[]
                }
            }
        }
    }[]>
    stacks: Map<number, {
        name: string
        layers: {
            T: {
                id: number
                attr: string
                internalID: number
                attrX: boolean
                attrY: boolean
                attrZ: boolean
                containerBoneID: number
                containerID: number
                curves: {
                    x: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    y: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    z: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                }
            }
            R: {
                id: number
                attr: string
                internalID: number
                attrX: boolean
                attrY: boolean
                attrZ: boolean
                containerBoneID: number
                containerID: number
                curves: {
                    x: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    y: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    z: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                }
            }
            S: {
                id: number
                attr: string
                internalID: number
                attrX: boolean
                attrY: boolean
                attrZ: boolean
                containerBoneID: number
                containerID: number
                curves: {
                    x: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    y: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                    z: {
                        version: any
                        id: number
                        internalID: number
                        times: number[]
                        values: number[]
                        attrFlag: number[]
                        attrData: number[]
                    }
                }
            }
        }[][]
        length: number
        frames: number
    }>
    length: number
    fps: number
    frames: number
}} animations,
 * @param {{skeleton: { bones: THREE.Bone[]}}} group
"""
def addAnimations( group, animations ):

    if group.animations == undefined ):

        group.animations = []

    }

    stacks = animations.stacks

    for ( key in stacks ):

        stack = stacks[ key ]

        """
         * @type {{
         * name: string,
         * fps: number,
         * length: number,
         * hierarchy: Array.<{
         *     parent: number,
         *     name: string,
         *     keys: Array.<{
         *         time: number,
         *         pos: Array.<number>,
         *         rot: Array.<number>,
         *         scl: Array.<number>
         *     }>
         * }>
         * }}
        """
        animationData = {
            name: stack.name,
            fps: 30,
            length: stack.length,
            hierarchy: []
        }

        bones = group.skeleton.bones

        for ( bonesIndex = 0, bonesLength = bones.length; bonesIndex < bonesLength; ++ bonesIndex ):

            bone = bones[ bonesIndex ]

            name = bone.name.replace( /.*:/, '' )
            parentIndex = findIndex( bones, def ( parentBone ):

                return bone.parent == parentBone

            } )
            animationData.hierarchy.append( { parent: parentIndex, name: name, keys: [] } )

        }

        for ( frame = 0; frame <= stack.frames; frame ++ ):

            for ( bonesIndex = 0, bonesLength = bones.length; bonesIndex < bonesLength; ++ bonesIndex ):

                bone = bones[ bonesIndex ]
                boneIndex = bonesIndex

                animationNode = stack.layers[ 0 ][ boneIndex ]

                for ( hierarchyIndex = 0, hierarchyLength = animationData.hierarchy.length; hierarchyIndex < hierarchyLength; ++ hierarchyIndex ):

                    node = animationData.hierarchy[ hierarchyIndex ]

                    if node.name == bone.name ):

                        node.keys.append( generateKey( animations, animationNode, bone, frame ) )

                    }

                }

            }

        }

        group.animations.append( THREE.AnimationClip.parseAnimation( animationData, bones ) )

    }

}

euler = THREE.Euler()
quaternion = THREE.Quaternion()

"""
 * @param {THREE.Bone} bone
"""
def generateKey( animations, animationNode, bone, frame ):

    key = {
        time: frame / animations.fps,
        pos: bone.position.toArray(),
        rot: bone.quaternion.toArray(),
        scl: bone.scale.toArray()
    }

    if animationNode == undefined ) return key

    try {

        if hasCurve( animationNode, 'T' ) and hasKeyOnFrame( animationNode.T, frame ) ):

            key.pos = [ animationNode.T.curves.x.values[ frame ], animationNode.T.curves.y.values[ frame ], animationNode.T.curves.z.values[ frame ] ]

        }

        if hasCurve( animationNode, 'R' ) and hasKeyOnFrame( animationNode.R, frame ) ):

            rotationX = animationNode.R.curves.x.values[ frame ]
            rotationY = animationNode.R.curves.y.values[ frame ]
            rotationZ = animationNode.R.curves.z.values[ frame ]

            quaternion.setFromEuler( euler.set( rotationX, rotationY, rotationZ, 'ZYX' ) )
            key.rot = quaternion.toArray()

        }

        if hasCurve( animationNode, 'S' ) and hasKeyOnFrame( animationNode.S, frame ) ):

            key.scl = [ animationNode.S.curves.x.values[ frame ], animationNode.S.curves.y.values[ frame ], animationNode.S.curves.z.values[ frame ] ]

        }

    } catch ( error ):

        # Curve is not fully plotted.
        console.log( 'THREE.FBXLoader: ', bone )
        console.log( 'THREE.FBXLoader: ', error )

    }

    return key

}

AXES = [ 'x', 'y', 'z' ]

def hasCurve( animationNode, attribute ):

    if animationNode == undefined ):

        return false

    }

    attributeNode = animationNode[ attribute ]

    if ! attributeNode ):

        return false

    }

    return AXES.every( def ( key ):

        return attributeNode.curves[ key ] !== null

    } )

}

def hasKeyOnFrame( attributeNode, frame ):

    return AXES.every( def ( key ):

        return isKeyExistOnFrame( attributeNode.curves[ key ], frame )

    } )

}

def isKeyExistOnFrame( curve, frame ):

    return curve.values[ frame ] is not None

}

"""
 * An instance of a Vertex with data for drawing vertices to the screen.
 * @constructor
"""
def Vertex():

    """
     * Position of the vertex.
     * @type {THREE.Vector3}
    """
    self.position = THREE.Vector3()

    """
     * Normal of the vertex
     * @type {THREE.Vector3}
    """
    self.normal = THREE.Vector3()

    """
     * UV coordinates of the vertex.
     * @type {THREE.Vector2}
    """
    self.uv = THREE.Vector2()

    """
     * Color of the vertex
     * @type {THREE.Vector3}
    """
    self.color = THREE.Vector3()

    """
     * Indices of the bones vertex is influenced by.
     * @type {THREE.Vector4}
    """
    self.skinIndices = THREE.Vector4( 0, 0, 0, 0 )

    """
     * Weights that each bone influences the vertex.
     * @type {THREE.Vector4}
    """
    self.skinWeights = THREE.Vector4( 0, 0, 0, 0 )

}

Object.assign( Vertex.prototype, {

    copy(self, target ):

        return= target || Vertex()

        returnVar.position.copy( self.position )
        returnVar.normal.copy( self.normal )
        returnVar.uv.copy( self.uv )
        returnVar.skinIndices.copy( self.skinIndices )
        returnVar.skinWeights.copy( self.skinWeights )

        return returnVar

    },

    flattenToBuffers(self, vertexBuffer, normalBuffer, uvBuffer, colorBuffer, skinIndexBuffer, skinWeightBuffer ):

        self.position.toArray( vertexBuffer, vertexBuffer.length )
        self.normal.toArray( normalBuffer, normalBuffer.length )
        self.uv.toArray( uvBuffer, uvBuffer.length )
        self.color.toArray( colorBuffer, colorBuffer.length )
        self.skinIndices.toArray( skinIndexBuffer, skinIndexBuffer.length )
        self.skinWeights.toArray( skinWeightBuffer, skinWeightBuffer.length )

    }

} )

"""
 * @constructor
"""
def Triangle():

    """
     * @type {{position: THREE.Vector3, normal: THREE.Vector3, uv: THREE.Vector2, skinIndices: THREE.Vector4, skinWeights: THREE.Vector4}[]}
    """
    self.vertices = []

}

Object.assign( Triangle.prototype, {

    copy(self, target ):

        return= target || Triangle()

        for ( i = 0; i < self.vertices.length; ++ i ):

             self.vertices[ i ].copy( returnVar.vertices[ i ] )

        }

        return returnVar

    },

    flattenToBuffers(self, vertexBuffer, normalBuffer, uvBuffer, colorBuffer, skinIndexBuffer, skinWeightBuffer ):

        vertices = self.vertices

        for ( i = 0, l = vertices.length; i < l; ++ i ):

            vertices[ i ].flattenToBuffers( vertexBuffer, normalBuffer, uvBuffer, colorBuffer, skinIndexBuffer, skinWeightBuffer )

        }

    }

} )

"""
 * @constructor
"""
def Face():

    """
     * @type {{vertices: {position: THREE.Vector3, normal: THREE.Vector3, uv: THREE.Vector2, skinIndices: THREE.Vector4, skinWeights: THREE.Vector4}[]}[]}
    """
    self.triangles = []
    self.materialIndex = 0

}

Object.assign( Face.prototype, {

    copy(self, target ):

        return= target || Face()

        for ( i = 0; i < self.triangles.length; ++ i ):

            self.triangles[ i ].copy( returnVar.triangles[ i ] )

        }

        returnVar.materialIndex = self.materialIndex

        return returnVar

    },

    genTrianglesFromVertices(self, vertexArray ):

        for ( i = 2; i < vertexArray.length; ++ i ):

            triangle = Triangle()
            triangle.vertices[ 0 ] = vertexArray[ 0 ]
            triangle.vertices[ 1 ] = vertexArray[ i - 1 ]
            triangle.vertices[ 2 ] = vertexArray[ i ]
            self.triangles.append( triangle )

        }

    },

    flattenToBuffers(self, vertexBuffer, normalBuffer, uvBuffer, colorBuffer, skinIndexBuffer, skinWeightBuffer, materialIndexBuffer ):

        triangles = self.triangles
        materialIndex = self.materialIndex

        for ( i = 0, l = triangles.length; i < l; ++ i ):

            triangles[ i ].flattenToBuffers( vertexBuffer, normalBuffer, uvBuffer, colorBuffer, skinIndexBuffer, skinWeightBuffer )
            append( materialIndexBuffer, [ materialIndex, materialIndex, materialIndex ] )

        }

    }

} )

"""
 * @constructor
"""
def Geometry():

    """
     * @type {{triangles: {vertices: {position: THREE.Vector3, normal: THREE.Vector3, uv: THREE.Vector2, skinIndices: THREE.Vector4, skinWeights: THREE.Vector4}[]}[], materialIndex: number}[]}
    """
    self.faces = []

    """
     * @type {{}|THREE.Skeleton}
    """
    self.skeleton = null

}

Object.assign( Geometry.prototype, {

    """
     * @returns    {{vertexBuffer: number[], normalBuffer: number[], uvBuffer: number[], skinIndexBuffer: number[], skinWeightBuffer: number[], materialIndexBuffer: number[]}}
    """
    flattenToBuffers(self):

        vertexBuffer = []
        normalBuffer = []
        uvBuffer = []
        colorBuffer = []
        skinIndexBuffer = []
        skinWeightBuffer = []

        materialIndexBuffer = []

        faces = self.faces

        for ( i = 0, l = faces.length; i < l; ++ i ):

            faces[ i ].flattenToBuffers( vertexBuffer, normalBuffer, uvBuffer, colorBuffer, skinIndexBuffer, skinWeightBuffer, materialIndexBuffer )

        }

        return {
            vertexBuffer: vertexBuffer,
            normalBuffer: normalBuffer,
            uvBuffer: uvBuffer,
            colorBuffer: colorBuffer,
            skinIndexBuffer: skinIndexBuffer,
            skinWeightBuffer: skinWeightBuffer,
            materialIndexBuffer: materialIndexBuffer
        }

    }

} )

def TextParser() {}

Object.assign( TextParser.prototype, {

    getPrevNode(self):

        return self.nodeStack[ self.currentIndent - 2 ]

    },

    getCurrentNode(self):

        return self.nodeStack[ self.currentIndent - 1 ]

    },

    getCurrentProp(self):

        return self.currentProp

    },

    pushStack(self, node ):

        self.nodeStack.append( node )
        self.currentIndent += 1

    },

    popStack(self):

        self.nodeStack.pop()
        self.currentIndent -= 1

    },

    setCurrentProp(self, val, name ):

        self.currentProp = val
        self.currentPropName = name

    },

    # ----------parse ---------------------------------------------------
    parse(self, text ):

        self.currentIndent = 0
        self.allNodes = FBXTree()
        self.nodeStack = []
        self.currentProp = []
        self.currentPropName = ''

        split = text.split( '\n' )

        for ( lineNum = 0, lineLength = split.length; lineNum < lineLength; lineNum ++ ):

            l = split[ lineNum ]

            # skip comment line
            if l.match( /^[\s\t]*;/ ) ):

                continue

            }

            # skip empty line
            if l.match( /^[\s\t]*$/ ) ):

                continue

            }

            # beginning of node
            beginningOfNodeExp = RegExp( '^\\t{' + self.currentIndent + '}(\\w+):(.*){', '' )
            match = l.match( beginningOfNodeExp )

            if match ):

                nodeName = match[ 1 ].trim().replace( /^"/, '' ).replace( /"$/, '' )
                nodeAttrs = match[ 2 ].split( ',' )

                for ( i = 0, l = nodeAttrs.length; i < l; i ++ ):
                    nodeAttrs[ i ] = nodeAttrs[ i ].trim().replace( /^"/, '' ).replace( /"$/, '' )
                }

                self.parseNodeBegin( l, nodeName, nodeAttrs || null )
                continue

            }

            # node's property
            propExp = RegExp( '^\\t{' + ( self.currentIndent ) + '}(\\w+):[\\s\\t\\r\\n](.*)' )
            match = l.match( propExp )

            if match ):

                propName = match[ 1 ].replace( /^"/, '' ).replace( /"$/, '' ).trim()
                propValue = match[ 2 ].replace( /^"/, '' ).replace( /"$/, '' ).trim()

                # for special case: base64 image data follows "Content: ," line
                #    Content: ,
                #     "iVB..."
                if propName == 'Content' and propValue == ',' ):

                    propValue = split[ ++ lineNum ].replace( /"/g, '' ).trim()

                }

                self.parseNodeProperty( l, propName, propValue )
                continue

            }

            # end of node
            endOfNodeExp = RegExp( '^\\t{' + ( self.currentIndent - 1 ) + '}}' )

            if l.match( endOfNodeExp ) ):

                self.nodeEnd()
                continue

            }

            # for special case,
            #
            #      Vertices: *8670 {
            #          a: 0.0356229953467846,13.9599733352661,-0.399196773.....(snip)
            # -0.0612030513584614,13.960485458374,-0.409748703241348,-0.10.....
            # 0.12490539252758,13.7450733184814,-0.454119384288788,0.09272.....
            # 0.0836158767342567,13.5432004928589,-0.435397416353226,0.028.....
            #
            # these case the lines must contiue with previous line
            if l.match( /^[^\s\t}]/ ) ):

                self.parseNodePropertyContinued( l )

            }

        }

        return self.allNodes

    },

    parseNodeBegin(self, line, nodeName, nodeAttrs ):

        # nodeName = match[1]
        node = { 'name': nodeName, properties: {}, 'subNodes': {} }
        attrs = self.parseNodeAttr( nodeAttrs )
        currentNode = self.getCurrentNode()

        # a top node
        if self.currentIndent == 0 ):

            self.allNodes.add( nodeName, node )

        else:

            # a subnode

            # already exists subnode, then append it
            if nodeName in currentNode.subNodes ):

                tmp = currentNode.subNodes[ nodeName ]

                # console.log( "duped entry found\nkey: " + nodeName + "\nvalue: " + propValue )
                if self.isFlattenNode( currentNode.subNodes[ nodeName ] ) ):


                    if attrs.id == '' ):

                        currentNode.subNodes[ nodeName ] = []
                        currentNode.subNodes[ nodeName ].append( tmp )

                    else:

                        currentNode.subNodes[ nodeName ] = {}
                        currentNode.subNodes[ nodeName ][ tmp.id ] = tmp

                    }

                }

                if attrs.id == '' ):

                    currentNode.subNodes[ nodeName ].append( node )

                else:

                    currentNode.subNodes[ nodeName ][ attrs.id ] = node

                }

            elif typeof attrs.id == 'number' || attrs.id.match( /^\d+$/ ) ):

                currentNode.subNodes[ nodeName ] = {}
                currentNode.subNodes[ nodeName ][ attrs.id ] = node

            else:

                currentNode.subNodes[ nodeName ] = node

            }

        }

        # for this          ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        # NodeAttribute: 1001463072, "NodeAttribute::", "LimbNode" {
        if nodeAttrs ):

            node.id = attrs.id
            node.attrName = attrs.name
            node.attrType = attrs.type

        }

        self.appendStack( node )

    },

    parseNodeAttr(self, attrs ):

        id = attrs[ 0 ]

        if attrs[ 0 ] !== '' ):

            id = parseInt( attrs[ 0 ] )

            if isNaN( id ) ):

                # PolygonVertexIndex: *16380 {
                id = attrs[ 0 ]

            }

        }

        name = '', type = ''

        if attrs.length > 1 ):

            name = attrs[ 1 ].replace( /^(\w+)::/, '' )
            type = attrs[ 2 ]

        }

        return { id: id, name: name, type: type }

    },

    parseNodeProperty(self, line, propName, propValue ):

        currentNode = self.getCurrentNode()
        parentName = currentNode.name

        # special case parent node's is like "Properties70"
        # these children nodes must treat with careful
        if parentName is not None ):

            propMatch = parentName.match( /Properties(\d)+/ )
            if propMatch ):

                self.parseNodeSpecialProperty( line, propName, propValue )
                return

            }

        }

        # special case Connections
        if propName == 'C' ):

            connProps = propValue.split( ',' ).slice( 1 )
            from = parseInt( connProps[ 0 ] )
            to = parseInt( connProps[ 1 ] )

            rest = propValue.split( ',' ).slice( 3 )

            propName = 'connections'
            propValue = [ from, to ]
            append( propValue, rest )

            if currentNode.properties[ propName ] == undefined ):

                currentNode.properties[ propName ] = []

            }

        }

        # special case Connections
        if propName == 'Node' ):

            id = parseInt( propValue )
            currentNode.properties.id = id
            currentNode.id = id

        }

        # already exists in properties, then append this
        if propName in currentNode.properties ):

            # console.log( "duped entry found\nkey: " + propName + "\nvalue: " + propValue )
            if Array.isArray( currentNode.properties[ propName ] ) ):

                currentNode.properties[ propName ].append( propValue )

            else:

                currentNode.properties[ propName ] += propValue

            }

        else:

            # console.log( propName + ":  " + propValue )
            if Array.isArray( currentNode.properties[ propName ] ) ):

                currentNode.properties[ propName ].append( propValue )

            else:

                currentNode.properties[ propName ] = propValue

            }

        }

        self.setCurrentProp( currentNode.properties, propName )

    },

    # TODO:
    parseNodePropertyContinued(self, line ):

        self.currentProp[ self.currentPropName ] += line

    },

    parseNodeSpecialProperty(self, line, propName, propValue ):

        # split this
        # P: "Lcl Scaling", "Lcl Scaling", "", "A",1,1,1
        # into array like below
        # ["Lcl Scaling", "Lcl Scaling", "", "A", "1,1,1" ]
        props = propValue.split( '",' )

        for ( i = 0, l = props.length; i < l; i ++ ):
            props[ i ] = props[ i ].trim().replace( /^\"/, '' ).replace( /\s/, '_' )
        }

        innerPropName = props[ 0 ]
        innerPropType1 = props[ 1 ]
        innerPropType2 = props[ 2 ]
        innerPropFlag = props[ 3 ]
        innerPropValue = props[ 4 ]

        /*
        if innerPropValue == undefined ):
            innerPropValue = props[3]
        }
        */

        # cast value in its type
        switch ( innerPropType1 ):

            case 'int':
                innerPropValue = parseInt( innerPropValue )
                break

            case 'double':
                innerPropValue = parseFloat( innerPropValue )
                break

            case 'ColorRGB':
            case 'Vector3D':
                innerPropValue = parseFloatArray( innerPropValue )
                break

        }

        # CAUTION: these props must append to parent's parent
        self.getPrevNode().properties[ innerPropName ] = {

            'type': innerPropType1,
            'type2': innerPropType2,
            'flag': innerPropFlag,
            'value': innerPropValue

        }

        self.setCurrentProp( self.getPrevNode().properties, innerPropName )

    },

    nodeEnd(self):

        self.popStack()

    },

    /* ----------------------------------------------------------------"""
    /*        util                                                     """
    isFlattenNode(self, node ):

        return ( 'subNodes' in node and 'properties' in node ) ? true : false

    }

} )

# Binary format specification:
#   https:#code.blender.org/2013/08/fbx-binary-file-format-specification/
#   https:#wiki.rogiken.org/specifications/file-format/fbx/ (more detail but Japanese)
def BinaryParser() {}

Object.assign( BinaryParser.prototype, {

    """
     * Parses binary data and builds FBXTree as much compatible as possible with the one built by TextParser.
     * @param {ArrayBuffer} buffer
     * @returns {THREE.FBXTree}
    """
    parse(self, buffer ):

        reader = BinaryReader( buffer )
        reader.skip( 23 ); # skip magic 23 bytes

        version = reader.getUint32()

        console.log( 'THREE.FBXLoader: FBX binary version: ' + version )

        allNodes = FBXTree()

        while ( ! self.endOfContent( reader ) ):

            node = self.parseNode( reader, version )
            if node !== null ) allNodes.add( node.name, node )

        }

        return allNodes

    },

    """
     * Checks if reader has reached the end of content.
     * @param {BinaryReader} reader
     * @returns {boolean}
    """
    endOfContent: function( reader ):

        # footer size: 160bytes + 16-byte alignment padding
        # - 16bytes: magic
        # - padding til 16-byte alignment (at least 1byte?)
        #   (seems like some exporters embed fixed 15 or 16bytes?)
        # - 4bytes: magic
        # - 4bytes: version
        # - 120bytes: zero
        # - 16bytes: magic
        if reader.size() % 16 == 0 ):

            return ( ( reader.getOffset() + 160 + 16 ) & ~0xf ) >= reader.size()

        else:

            return reader.getOffset() + 160 + 16 >= reader.size()

        }

    },

    """
     * Parses Node as much compatible as possible with the one parsed by TextParser
     * TODO: could be optimized more?
     * @param {BinaryReader} reader
     * @param {number} version
     * @returns {Object} - Returns an Object as node, or null if NULL-record.
    """
    parseNode(self, reader, version ):

        # The first three data sizes depends on version.
        endOffset = ( version >= 7500 ) ? reader.getUint64() : reader.getUint32()
        numProperties = ( version >= 7500 ) ? reader.getUint64() : reader.getUint32()
        propertyListLen = ( version >= 7500 ) ? reader.getUint64() : reader.getUint32()
        nameLen = reader.getUint8()
        name = reader.getString( nameLen )

        # Regards this node as NULL-record if endOffset is zero
        if endOffset == 0 ) return null

        propertyList = []

        for ( i = 0; i < numProperties; i ++ ):

            propertyList.append( self.parseProperty( reader ) )

        }

        # Regards the first three elements in propertyList as id, attrName, and attrType
        id = propertyList.length > 0 ? propertyList[ 0 ] : ''
        attrName = propertyList.length > 1 ? propertyList[ 1 ] : ''
        attrType = propertyList.length > 2 ? propertyList[ 2 ] : ''

        subNodes = {}
        properties = {}

        isSingleProperty = false

        # if this node represents just a single property
        # like (name, 0) set or (name2, [0, 1, 2]) set of {name: 0, name2: [0, 1, 2]}
        if numProperties == 1 and reader.getOffset() == endOffset ):

            isSingleProperty = true

        }

        while ( endOffset > reader.getOffset() ):

            node = self.parseNode( reader, version )

            if node is None ) continue

            # special case: child node is single property
            if node.singleProperty:

                value = node.propertyList[ 0 ]

                if Array.isArray( value ):

                    # node represents
                    #    Vertices: *3 {
                    #        a: 0.01, 0.02, 0.03
                    #    }
                    # of text format here.

                    node.properties[ node.name ] = node.propertyList[ 0 ]
                    subNodes[ node.name ] = node

                    # Later phase expects single property array is in node.properties.a as String.
                    # TODO: optimize
                    node.properties.a = value.toString()

                else:

                    # node represents
                    #     Version: 100
                    # of text format here.

                    properties[ node.name ] = value

                }

                continue

            }

            # special case: connections
            if name == 'Connections' and node.name == 'C' ):

                array = []

                # node.propertyList would be like
                # ["OO", 111264976, 144038752, "d|x"] (?, from, to, additional values)
                for ( i = 1, il = node.propertyList.length; i < il; i ++ ):

                    array[ i - 1 ] = node.propertyList[ i ]

                }

                if properties.connections == undefined ):

                    properties.connections = []

                }

                properties.connections.append( array )

                continue

            }

            # special case: child node is Properties\d+
            if node.name.match( /^Properties\d+$/ ) ):

                # move child node's properties to this node.

                keys = Object.keys( node.properties )

                for ( i = 0, il = keys.length; i < il; i ++ ):

                    key = keys[ i ]
                    properties[ key ] = node.properties[ key ]

                }

                continue

            }

            # special case: properties
            if name.match( /^Properties\d+$/ ) and node.name == 'P' ):

                innerPropName = node.propertyList[ 0 ]
                innerPropType1 = node.propertyList[ 1 ]
                innerPropType2 = node.propertyList[ 2 ]
                innerPropFlag = node.propertyList[ 3 ]
                innerPropValue

                if innerPropName.indexOf( 'Lcl ' ) == 0 ) innerPropName = innerPropName.replace( 'Lcl ', 'Lcl_' )
                if innerPropType1.indexOf( 'Lcl ' ) == 0 ) innerPropType1 = innerPropType1.replace( 'Lcl ', 'Lcl_' )

                if innerPropType1 == 'ColorRGB' || innerPropType1 == 'Vector' ||
                     innerPropType1 == 'Vector3D' || innerPropType1.indexOf( 'Lcl_' ) == 0 ):

                    innerPropValue = [
                        node.propertyList[ 4 ],
                        node.propertyList[ 5 ],
                        node.propertyList[ 6 ]
                    ]

                else:

                    innerPropValue = node.propertyList[ 4 ]

                }

                if innerPropType1.indexOf( 'Lcl_' ) == 0 ):

                    innerPropValue = innerPropValue.toString()

                }

                # this will be copied to parent. see above.
                properties[ innerPropName ] = {

                    'type': innerPropType1,
                    'type2': innerPropType2,
                    'flag': innerPropFlag,
                    'value': innerPropValue

                }

                continue

            }

            # standard case
            # follows TextParser's manner.
            if subNodes[ node.name ] == undefined ):

                if typeof node.id == 'number' ):

                    subNodes[ node.name ] = {}
                    subNodes[ node.name ][ node.id ] = node

                else:

                    subNodes[ node.name ] = node

                }

            else:

                if node.id == '' ):

                    if ! Array.isArray( subNodes[ node.name ] ) ):

                        subNodes[ node.name ] = [ subNodes[ node.name ] ]

                    }

                    subNodes[ node.name ].append( node )

                else:

                    if subNodes[ node.name ][ node.id ] == undefined ):

                        subNodes[ node.name ][ node.id ] = node

                    else:

                        # conflict id. irregular?

                        if ! Array.isArray( subNodes[ node.name ][ node.id ] ) ):

                            subNodes[ node.name ][ node.id ] = [ subNodes[ node.name ][ node.id ] ]

                        }

                        subNodes[ node.name ][ node.id ].append( node )

                    }

                }

            }

        }

        return {

            singleProperty: isSingleProperty,
            id: id,
            attrName: attrName,
            attrType: attrType,
            name: name,
            properties: properties,
            propertyList: propertyList, # raw property list, would be used by parent
            subNodes: subNodes

        }

    },

    parseProperty(self, reader ):

        type = reader.getChar()

        switch ( type ):

            case 'F':
                return reader.getFloat32()

            case 'D':
                return reader.getFloat64()

            case 'L':
                return reader.getInt64()

            case 'I':
                return reader.getInt32()

            case 'Y':
                return reader.getInt16()

            case 'C':
                return reader.getBoolean()

            case 'f':
            case 'd':
            case 'l':
            case 'i':
            case 'b':

                arrayLength = reader.getUint32()
                encoding = reader.getUint32(); # 0: non-compressed, 1: compressed
                compressedLength = reader.getUint32()

                if encoding == 0 ):

                    switch ( type ):

                        case 'f':
                            return reader.getFloat32Array( arrayLength )

                        case 'd':
                            return reader.getFloat64Array( arrayLength )

                        case 'l':
                            return reader.getInt64Array( arrayLength )

                        case 'i':
                            return reader.getInt32Array( arrayLength )

                        case 'b':
                            return reader.getBooleanArray( arrayLength )

                    }

                }

                if window.Zlib == undefined ):

                    throw Error( 'THREE.FBXLoader: External library Inflate.min.js required, obtain or import from https:#github.com/imaya/zlib.js' )

                }

                inflate = Zlib.Inflate( Uint8Array( reader.getArrayBuffer( compressedLength ) ) )
                reader2 = BinaryReader( inflate.decompress().buffer )

                switch ( type ):

                    case 'f':
                        return reader2.getFloat32Array( arrayLength )

                    case 'd':
                        return reader2.getFloat64Array( arrayLength )

                    case 'l':
                        return reader2.getInt64Array( arrayLength )

                    case 'i':
                        return reader2.getInt32Array( arrayLength )

                    case 'b':
                        return reader2.getBooleanArray( arrayLength )

                }

            case 'S':
                length = reader.getUint32()
                return reader.getString( length )

            case 'R':
                length = reader.getUint32()
                return reader.getArrayBuffer( length )

            default:
                throw Error( 'THREE.FBXLoader: Unknown property type ' + type )

        }

    }

} )


def BinaryReader( buffer, littleEndian ):

    self.dv = DataView( buffer )
    self.offset = 0
    self.littleEndian = ( littleEndian is not None ) ? littleEndian : true

}

Object.assign( BinaryReader.prototype, {

    getOffset(self):

        return self.offset

    },

    size(self):

        return self.dv.buffer.byteLength

    },

    skip(self, length ):

        self.offset += length

    },

    # seems like true/false representation depends on exporter.
    #   true: 1 or 'Y'(=0x59), false: 0 or 'T'(=0x54)
    # then sees LSB.
    getBoolean(self):

        return ( self.getUint8() & 1 ) == 1

    },

    getBooleanArray(self, size ):

        a = []

        for ( i = 0; i < size; i ++ ):

            a.append( self.getBoolean() )

        }

        return a

    },

    getInt8(self):

        value = self.dv.getInt8( self.offset )
        self.offset += 1
        return value

    },

    getInt8Array(self, size ):

        a = []

        for ( i = 0; i < size; i ++ ):

            a.append( self.getInt8() )

        }

        return a

    },

    getUint8(self):

        value = self.dv.getUint8( self.offset )
        self.offset += 1
        return value

    },

    getUint8Array(self, size ):

        a = []

        for ( i = 0; i < size; i ++ ):

            a.append( self.getUint8() )

        }

        return a

    },

    getInt16(self):

        value = self.dv.getInt16( self.offset, self.littleEndian )
        self.offset += 2
        return value

    },

    getInt16Array(self, size ):

        a = []

        for ( i = 0; i < size; i ++ ):

            a.append( self.getInt16() )

        }

        return a

    },

    getUint16(self):

        value = self.dv.getUint16( self.offset, self.littleEndian )
        self.offset += 2
        return value

    },

    getUint16Array(self, size ):

        a = []

        for ( i = 0; i < size; i ++ ):

            a.append( self.getUint16() )

        }

        return a

    },

    getInt32(self):

        value = self.dv.getInt32( self.offset, self.littleEndian )
        self.offset += 4
        return value

    },

    getInt32Array(self, size ):

        a = []

        for ( i = 0; i < size; i ++ ):

            a.append( self.getInt32() )

        }

        return a

    },

    getUint32(self):

        value = self.dv.getUint32( self.offset, self.littleEndian )
        self.offset += 4
        return value

    },

    getUint32Array(self, size ):

        a = []

        for ( i = 0; i < size; i ++ ):

            a.append( self.getUint32() )

        }

        return a

    },

    # JavaScript doesn't support 64-bit integer so attempting to calculate by ourselves.
    # 1 << 32 will return 1 so using multiply operation instead here.
    # There'd be a possibility that this method returns wrong value if the value
    # is out of the range between Number.MAX_SAFE_INTEGER and Number.MIN_SAFE_INTEGER.
    # TODO: safely handle 64-bit integer
    getInt64(self):

        low, high

        if self.littleEndian ):

            low = self.getUint32()
            high = self.getUint32()

        else:

            high = self.getUint32()
            low = self.getUint32()

        }

        # calculate negative value
        if high & 0x80000000 ):

            high = ~high & 0xFFFFFFFF
            low = ~low & 0xFFFFFFFF

            if low == 0xFFFFFFFF ) high = ( high + 1 ) & 0xFFFFFFFF

            low = ( low + 1 ) & 0xFFFFFFFF

            return - ( high * 0x100000000 + low )

        }

        return high * 0x100000000 + low

    },

    getInt64Array(self, size ):

        a = []

        for ( i = 0; i < size; i ++ ):

            a.append( self.getInt64() )

        }

        return a

    },

    # Note: see getInt64() comment
    getUint64(self):

        low, high

        if self.littleEndian ):

            low = self.getUint32()
            high = self.getUint32()

        else:

            high = self.getUint32()
            low = self.getUint32()

        }

        return high * 0x100000000 + low

    },

    getUint64Array(self, size ):

        a = []

        for ( i = 0; i < size; i ++ ):

            a.append( self.getUint64() )

        }

        return a

    },

    getFloat32(self):

        value = self.dv.getFloat32( self.offset, self.littleEndian )
        self.offset += 4
        return value

    },

    getFloat32Array(self, size ):

        a = []

        for ( i = 0; i < size; i ++ ):

            a.append( self.getFloat32() )

        }

        return a

    },

    getFloat64(self):

        value = self.dv.getFloat64( self.offset, self.littleEndian )
        self.offset += 8
        return value

    },

    getFloat64Array(self, size ):

        a = []

        for ( i = 0; i < size; i ++ ):

            a.append( self.getFloat64() )

        }

        return a

    },

    getArrayBuffer(self, size ):

        value = self.dv.buffer.slice( self.offset, self.offset + size )
        self.offset += size
        return value

    },

    getChar(self):

        return String.fromCharCode( self.getUint8() )

    },

    getString(self, size ):

        s = ''

        while ( size > 0 ):

            value = self.getUint8()
            size--

            if value == 0 ) break

            s += String.fromCharCode( value )

        }

        self.skip( size )

        return s

    }

} )


def FBXTree() {}

Object.assign( FBXTree.prototype, {

    add(self, key, val ):

        this[ key ] = val

    },

    searchConnectionParent(self, id ):

        if self.__cache_search_connection_parent == undefined ):

            self.__cache_search_connection_parent = []

        }

        if self.__cache_search_connection_parent[ id ] is not None ):

            return self.__cache_search_connection_parent[ id ]

        else:

            self.__cache_search_connection_parent[ id ] = []

        }

        conns = self.Connections.properties.connections

        results = []
        for ( i = 0; i < conns.length; ++ i ):

            if conns[ i ][ 0 ] == id ):

                # 0 means scene root
                res = conns[ i ][ 1 ] == 0 ? - 1 : conns[ i ][ 1 ]
                results.append( res )

            }

        }

        if results.length > 0 ):

            append( self.__cache_search_connection_parent[ id ], results )
            return results

        else:

            self.__cache_search_connection_parent[ id ] = [ - 1 ]
            return [ - 1 ]

        }

    },

    searchConnectionChildren(self, id ):

        if self.__cache_search_connection_children == undefined ):

            self.__cache_search_connection_children = []

        }

        if self.__cache_search_connection_children[ id ] is not None ):

            return self.__cache_search_connection_children[ id ]

        else:

            self.__cache_search_connection_children[ id ] = []

        }

        conns = self.Connections.properties.connections

        res = []
        for ( i = 0; i < conns.length; ++ i ):

            if conns[ i ][ 1 ] == id ):

                # 0 means scene root
                res.append( conns[ i ][ 0 ] == 0 ? - 1 : conns[ i ][ 0 ] )
                # there may more than one kid, then search to the end

            }

        }

        if res.length > 0 ):

            append( self.__cache_search_connection_children[ id ], res )
            return res

        else:

            self.__cache_search_connection_children[ id ] = [ ]
            return [ ]

        }

    },

    searchConnectionType(self, id, to ):

        key = id + ',' + to; # TODO: to hash
        if self.__cache_search_connection_type == undefined ):

            self.__cache_search_connection_type = {}

        }

        if self.__cache_search_connection_type[ key ] is not None ):

            return self.__cache_search_connection_type[ key ]

        else:

            self.__cache_search_connection_type[ key ] = ''

        }

        conns = self.Connections.properties.connections

        for ( i = 0; i < conns.length; ++ i ):

            if conns[ i ][ 0 ] == id and conns[ i ][ 1 ] == to ):

                # 0 means scene root
                self.__cache_search_connection_type[ key ] = conns[ i ][ 2 ]
                return conns[ i ][ 2 ]

            }

        }

        self.__cache_search_connection_type[ id ] = null
        return null

    }

} )


"""
 * @param {ArrayBuffer} buffer
 * @returns {boolean}
"""
def isFbxFormatBinary( buffer ):

    CORRECT = 'Kaydara FBX Binary  \0'

    return buffer.byteLength >= CORRECT.length and CORRECT == convertArrayBufferToString( buffer, 0, CORRECT.length )

}

"""
 * @returns {boolean}
"""
def isFbxFormatASCII( text ):

    CORRECT = [ 'K', 'a', 'y', 'd', 'a', 'r', 'a', '\\', 'F', 'B', 'X', '\\', 'B', 'i', 'n', 'a', 'r', 'y', '\\', '\\' ]

    cursor = 0

    def read( offset ):

        result = text[ offset - 1 ]
        text = text.slice( cursor + offset )
        cursor ++
        return result

    }

    for ( i = 0; i < CORRECT.length; ++ i ):

        num = read( 1 )
        if num == CORRECT[ i ] ):

            return false

        }

    }

    return true

}

"""
 * @returns {number}
"""
def getFbxVersion( text ):

    versionRegExp = /FBXVersion: (\d+)/
    match = text.match( versionRegExp )
    if match ):

        version = parseInt( match[ 1 ] )
        return version

    }
    throw Error( 'THREE.FBXLoader: Cannot find the version number for the file given.' )

}

"""
 * Converts FBX ticks into real time seconds.
 * @param {number} time - FBX tick timestamp to convert.
 * @returns {number} - FBX tick in real world time.
"""
def convertFBXTimeToSeconds( time ):

    # Constant is FBX ticks per second.
    return time / 46186158000

}

"""
 * Parses comma separated list of float numbers and returns them in an array.
 * @example
 * # Returns [ 5.6, 9.4, 2.5, 1.4 ]
 * parseFloatArray( "5.6,9.4,2.5,1.4" )
 * @returns {number[]}
"""
def parseFloatArray( string ):

    array = string.split( ',' )

    for ( i = 0, l = array.length; i < l; i ++ ):

        array[ i ] = parseFloat( array[ i ] )

    }

    return array

}

"""
 * Parses comma separated list of int numbers and returns them in an array.
 * @example
 * # Returns [ 5, 8, 2, 3 ]
 * parseFloatArray( "5,8,2,3" )
 * @returns {number[]}
"""
def parseIntArray( string ):

    array = string.split( ',' )

    for ( i = 0, l = array.length; i < l; i ++ ):

        array[ i ] = parseInt( array[ i ] )

    }

    return array

}

"""
 * Parses Vector3 property from FBXTree.  Property is given as .value.x, .value.y, etc.
 * @param {FBXVector3} property - Property to parse as Vector3.
 * @returns {THREE.Vector3}
"""
def parseVector3( property ):

    return THREE.Vector3().fromArray( property.value )

}

"""
 * Parses Color property from FBXTree.  Property is given as .value.x, .value.y, etc.
 * @param {FBXVector3} property - Property to parse as Color.
 * @returns {THREE.Color}
"""
def parseColor( property ):

    return THREE.Color().fromArray( property.value )

}

def parseMatrixArray( floatString ):

    return THREE.Matrix4().fromArray( parseFloatArray( floatString ) )

}

"""
 * Converts ArrayBuffer to String.
 * @param {ArrayBuffer} buffer
 * @param {number} from
 * @param {number} to
 * @returns {String}
"""
def convertArrayBufferToString( buffer, from, to ):

    if from == undefined ) from = 0
    if to == undefined ) to = buffer.byteLength

    array = Uint8Array( buffer, from, to )

    if window.TextDecoder is not None ):

        return TextDecoder().decode( array )

    }

    s = ''

    for ( i = 0, il = array.length; i < il; i ++ ):

        s += String.fromCharCode( array[ i ] )

    }

    return s

}

"""
 * Converts number from degrees into radians.
 * @param {number} value
 * @returns {number}
"""
def degreeToRadian( value ):

    return value * DEG2RAD

}

DEG2RAD = Math.PI / 180

#

def findIndex( array, func ):

    for ( i = 0, l = array.length; i < l; i ++ ):

        if func( array[ i ] ) ) return i

    }

    return -1

}

def append( a, b ):

    for ( i = 0, j = a.length, l = b.length; i < l; i ++, j ++ ):

        a[ j ] = b[ i ]

    }

}

def slice( a, b, from, to ):

    for ( i = from, j = 0; i < to; i ++, j ++ ):

        a[ j ] = b[ i ]

    }

    return a

}
