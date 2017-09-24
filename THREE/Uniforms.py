"""
    /**
     * @author tschw
     *
     * Uniforms of a program.
     * Those form a tree structure with a special top-level container for the root,
     * which you get by calling 'WebGLUniforms( gl, program, renderer )'.
     *
     *
     * Properties of inner nodes including the top-level container:
     *
     * .seq - array of nested uniforms
     * .map - nested uniforms by name
     *
     *
     * Methods of all nodes except the top-level container:
     *
     * .setValue( gl, value, [renderer] )
     *
     *         uploads a uniform value(s)
     *      the 'renderer' parameter is needed for sampler uniforms
     *
     *
     * Static methods of the top-level container (renderer factorizations):
     *
     * .upload( gl, seq, values, renderer )
     *
     *         sets uniforms in 'seq' to 'values[id].value'
     *
     * .seqWithValue( seq, values ) : filteredSeq
     *
     *         filters 'seq' entries with corresponding entry in values
     *
     *
     * Methods of the top-level container (renderer factorizations):
     *
     * .setValue( gl, name, value )
     *
     *         sets uniform with  name 'name' to 'value'
     *
     * .set( gl, obj, prop )
     *
     *         sets uniform from object and property with same name than uniform
     *
     * .setOptional( gl, obj, prop )
     *
     *         like .set for an optional property of the object
     *
     */
"""
import numpy as np
from OpenGL.GL import *
import re
from THREE.Texture import *
from THREE.CubeTexture import *


emptyTexture = Texture()
emptyCubeTexture = CubeTexture()

# // --- Base for inner nodes (including the root) ---


class UniformContainer():
    def __init__(self):
        self.seq = []
        self.map = {}

# // --- Utilities ---


class Uniform:
    def __init__(self, dic):
        if type in dic:
            self.type = dic['type']
        self.value = dic['value']
        if 'needsUpdate' in dic:
            self.needsUpdate = dic['needsUpdate']
        else:
            self.needsUpdate = True


class Uniforms:
    def __init__(self, lst):
        super().__setattr__('Uniforms', {})
        for uniform in lst:
            self.Uniforms[uniform] = Uniform(lst[uniform])

    def __getattr__(self, item):
        try:
            return self.Uniforms[item]
        except KeyError:
            raise AttributeError

    def __setattr__(self, key, value):
        self.Uniforms[key] = value

    def __delattr__(self, item):
        del self.Uniforms[item]

    def __iter__(self):
        return iter(self.Uniforms)

    def __getitem__(self, item):
        return self.Uniforms[item]


# // Array Caches (provide typed arrays for temporary by size)


arrayCacheF32 = [None for i in range(32)]
arrayCacheI32 = [None for i in range(32)]

# // Float32Array caches used for uploading Matrix uniforms

mat4array = np.zeros(16, 'f' )
mat3array = np.zeros( 9 , 'f')

# // Flattening for arrays of vectors and matrices

def flatten( array, nBlocks, blockSize ):
    firstElem = array[ 0 ]

    if isinstance(firstElem, float) or isinstance(firstElem, np.float32):
        return array
    # // unoptimized: ! isNaN( firstElem )
    # // see http:# //jacksondunstan.com/articles/983

    n = nBlocks * blockSize
    r = arrayCacheF32[n]

    if r is None:
        r = np.zeros(n, 'f')
        arrayCacheF32[n] = r

    if nBlocks != 0:
        firstElem.toArray( r, 0 )
        offset = 0
        for i in range(1,nBlocks):
            offset += blockSize
            array[ i ].toArray( r, offset )

    return r

# // Texture unit allocation

def allocTexUnits( renderer, n ):
    r = arrayCacheI32[n]

    if r is None:
        r = np.zeros( n , "l")
        arrayCacheI32.append(r)

    for i in range(n):
        r[ i ] = renderer.allocTextureUnit()

    return r

# // --- Setters ---

# // Note: Defining these methods externally, because they come in a bunch
# // and self way their names minify.

# // Helper to pick the right setter for the singular case

# // --- Uniform Classes ---


class SingleUniform:
    def __init__(self, id, activeInfo, addr ):
        self.id = id
        self.addr = addr

        _types = {
            0x1406: self.setValue1f,  # // FLOAT
            0x8b50: self.setValue2fv,  # // _VEC2
            0x8b51: self.setValue3fv,  # // _VEC3
            0x8b52: self.setValue4fv,  # // _VEC4

            0x8b5a: self.setValue2fm,  # // _MAT2
            0x8b5b: self.setValue3fm,  # // _MAT3
            0x8b5c: self.setValue4fm,  # // _MAT4

            0x8b5e: self.setValueT1,
            0x8d66: self.setValueT1,  # // SAMPLER_2D, SAMPLER_EXTERNAL_OES
            0x8b60: self.setValueT6,  # // SAMPLER_CUBE

            0x1404: self.setValue1i,
            0x8b56: self.setValue1i,  # // INT, BOOL
            0x8b53: self.setValue2iv,
            0x8b57: self.setValue2iv,  # // _VEC2
            0x8b54: self.setValue3iv,
            0x8b58: self.setValue3iv,  # // _VEC3
            0x8b55: self.setValue4iv,
            0x8b59: self.setValue4iv  # // _VEC4
        }

        v = _types[activeInfo[2]]
        self.setValue = v

    # // Single scalar

    def setValue1f(self, v, renderer=None):
        glUniform1f(self.addr, v)

    def setValue1i(self, v, renderer=None):
        glUniform1i(self.addr, v)

        # // Single float vector (from flat array or THREE.VectorN)

    def setValue2fv(self, v, renderer=None):
        if v.x is None:
            glUniform2fv(self.addr, v)
        else:
            glUniform2f(self.addr, v.x, v.y)

    def setValue3fv(self, v, renderer=None):
        if hasattr(v, 'x'):
            glUniform3f(self.addr, v.x, v.y, v.z)
        elif hasattr(v, 'r'):
            glUniform3f(self.addr, v.r, v.g, v.b)
        else:
            # TODO FDE: fix this ?
            # glUniform3f(self.addr, v[0], v[1], v[2])
            glUniform3fv(self.addr, 1, v)

    def setValue4fv(self, v, renderer=None):
        if hasattr(v, 'x') is None:
            glUniform4fv(self.addr, v)
        else:
            glUniform4f(self.addr, v.x, v.y, v.z, v.w)

    # // Single matrix (from flat array or MatrixN)

    def setValue2fm(self, v, renderer=None):
        glUniformMatrix2fv(self.addr, 1, GL_FALSE, v.elements or v)

    def setValue3fm(self, v, renderer=None):
        if v.elements is None:
            glUniformMatrix3fv(self.addr, GL_FALSE, v)
        else:
            mat3array = np.array(v.elements, 'f')
            glUniformMatrix3fv(self.addr, 1, GL_FALSE, mat3array)

    def setValue4fm(self, v, renderer=None):
        if v.elements is None:
            glUniformMatrix4fv(self.addr, GL_FALSE, v)
        else:
            # TODO reuse the mat4array numpy
            # mat4array.set(v.elements)
            mat4array = np.array(v.elements, 'f')
            glUniformMatrix4fv(self.addr, 1, GL_FALSE, mat4array)

    # // Single texture (2D / Cube)

    def setValueT1(self, v, renderer):
        unit = renderer.allocTextureUnit()
        glUniform1i(self.addr, unit)
        renderer.setTexture2D(v or emptyTexture, unit)

    def setValueT6(self, v, renderer):
        unit = renderer.allocTextureUnit()
        glUniform1i(self.addr, unit)
        renderer.setTextureCube(v or emptyCubeTexture, unit)

    # // Integer / Boolean vectors or arrays thereof (always flat arrays)

    def setValue2iv(self, v, renderer=None):
        glUniform2iv(self.addr, v)

    def setValue3iv(self, v, renderer=None):
        glUniform3iv(self.addr, v)

    def setValue4iv(self, v, renderer=None):
        glUniform4iv(self.addr, v)

    # // self.path = activeInfo.name; # // DEBUG

class PureArrayUniform():
    def __init__(self, id, activeInfo, addr ):
        self.id = id
        self.addr = addr
        self.size = activeInfo[1]
        # // Helper to pick the right setter for a pure (bottom-level) array
        _types = {
            0x1406: self.setValue1fv,  # // FLOAT
            0x8b50: self.setValueV2a,  # // _VEC2
            0x8b51: self.setValueV3a,  # // _VEC3
            0x8b52: self.setValueV4a,  # // _VEC4

            0x8b5a: self.setValueM2a,  # // _MAT2
            0x8b5b: self.setValueM3a,  # // _MAT3
            0x8b5c: self.setValueM4a,  # // _MAT4

            0x8b5e: self.setValueT1a,
            0x8d66: self.setValueT1a,  # // SAMPLER_2D, SAMPLER_EXTERNAL_OES
            0x8b60: self.setValueT6a,  # // SAMPLER_CUBE

            0x1404: self.setValue1iv,
            0x8b56: self.setValue1iv,  # // INT, BOOL
            0x8b53: self.setValue2iv,
            0x8b57: self.setValue2iv,  # // _VEC2
            0x8b54: self.setValue3iv,
            0x8b58: self.setValue3iv,  # // _VEC3
            0x8b55: self.setValue4iv,
            0x8b59: self.setValue4iv  # // _VEC4
        }

        self.setValue = _types[activeInfo[2]]

    # // Array of scalars

    def setValue1fv(self, v, renderer=None):
        glUniform1fv(self.addr, 1, v)

    def setValue1iv(self, v, renderer=None):
        glUniform1iv(self.addr, 1, v)

    def setValue2iv(self, v, renderer=None):
        glUniform2iv(self.addr, 1, v)

    def setValue3iv(self, v, renderer=None):
        glUniform3iv(self.addr, 1, v)

    def setValue4iv(self, v, renderer=None):
        glUniform4iv(self.addr, 1, v)

    # // Array of vectors (flat or from THREE classes)

    def setValueV2a(self, v, renderer=None):
        glUniform2fv(self.addr, len(v), flatten(v, self.size, 2))

    def setValueV3a(self, v, renderer=None):
        glUniform3fv(self.addr, len(v), flatten(v, self.size, 3))

    def setValueV4a(self, v, renderer=None):
        glUniform4fv(self.addr, len(v), flatten(v, self.size, 4))

    # // Array of matrices (flat or from THREE clases)

    def setValueM2a(self, v, renderer=None):
        glUniformMatrix2fv(self.addr, len(v), GL_FALSE, flatten(v, self.size, 4))

    def setValueM3a(self, v, renderer=None):
        glUniformMatrix3fv(self.addr, len(v), GL_FALSE, flatten(v, self.size, 9))

    def setValueM4a(self, v, renderer=None):
        glUniformMatrix4fv(self.addr, len(v), GL_FALSE, flatten(v, self.size, 16))

    # // Array of textures (2D / Cube)

    def setValueT1a(self, v, renderer):
        n = len(v)
        units = allocTexUnits(renderer, n)

        glUniform1iv(self.addr, n, units)

        for i in range(n):
            renderer.setTexture2D(v[i] or emptyTexture, units[i])

    def setValueT6a(self, v, renderer):
        n = len(v)
        units = allocTexUnits(renderer, n)

        glUniform1iv(self.addr, units)

        for i in range(n):
            renderer.setTextureCube(v[i] or emptyCubeTexture, units[i])

        # // self.path = activeInfo.name; # // DEBUG
    
    
class StructuredUniform( UniformContainer ):
    def __init__(self, id ):
        self.id = id
        super().__init__(  ) # // mix-in

    def setValue(self, value, renderer ):
        # // Note: Don't need an extra 'renderer' parameter, since samplers
        # // are not allowed in structured uniforms.
        seq = self.seq

        for i in range (len(seq)):
            u = seq[ i ]
            u.setValue( value[ u.id ], renderer )

# // --- Top-level ---

# // Parser - builds up the property tree from the path strings


_RePathPart = re.compile('([\w\d_]+)(\])?(\[|\.)?')

# // extracts
# //     - the identifier (member name or array index)
# //  - followed by an optional right bracket (found when array index)
# //  - followed by an optional left bracket or dot (type of subscript)
# //
# // Note: These portions can be read in a non-overlapping fashion and
# // allow straightforward parsing of the hierarchy that WebGL encodes
# // in the uniform names.


def addUniform( container, uniformObject ):
    container.seq.append( uniformObject )
    container.map[ uniformObject.id ] = uniformObject


def parseUniform( activeInfo, addr, container ):
    path = activeInfo[0].decode("utf-8")
    pathLength = len(path)

    # // reset RegExp object, because of the early exit of a previous run
#    _RePathPart.lastindex = 0

    pattern = '([\w\d_]+)(\])?(\[|\.)?'
    for match in re.finditer(pattern, path):
        matchEnd = match.regs[0][1]

        id = match.group(1)
        idIsIndex = match.group( 2 ) == ']'
        subscript = match.group( 3 )

        if idIsIndex:
            id = int(id)  # // convert to integer

        if subscript is None or subscript == '[' and matchEnd + 2 == pathLength:
            # // bare name or "pure" bottom-level array "[0]" suffix
            if subscript is None:
                uni = SingleUniform( id, activeInfo, addr )
            else:
                uni = PureArrayUniform( id, activeInfo, addr )

            addUniform( container, uni)
            break
        else:
            # // step into inner node / create it in case it doesn't exist
            map = container.map
            if id not in map:
                next = StructuredUniform( id )
                addUniform( container, next )
            else:
                next = map[id]

            container = next

# // Root Container


class pyOpenGLUniforms( UniformContainer ):
    def __init__( self, program, renderer ):
        super().__init__()

        self.renderer = renderer

        n = glGetProgramiv( program, GL_ACTIVE_UNIFORMS )

        for i in range(n):
            info = glGetActiveUniform( program, i )
            path = info[0]
            addr = glGetUniformLocation( program, path )

            parseUniform( info, addr, self )

    def setValue(self, gl, name, value ):
        if name in self.map:
            u = self.map[ name ]

            # TODO, what is self.renderer used for ?
            # u.setValue( value, self.renderer )
            u.setValue(value)

    def setOptional(self, gl, object, name ):
        if name in object:
            v = object[ name ]
            self.setValue( gl, name, v )

# // Static interface

    def upload(gl, seq, values, renderer ):
        for i in range(len(seq)):
            u = seq[ i ]
            v = values[ u.id ]

            if not v.needsUpdate == False:
                # // note: always updating when .needsUpdate is undefined
                u.setValue( v.value, renderer )

    def seqWithValue(seq, values):
        r = []

        for i in range(len(seq)):
            u = seq[ i ]
            if u.id in values:
                r.append( u )

        return r

