"""
/**
 * @author tschw
 * @author Mugen87 / https://github.com/Mugen87
 * @author mrdoob / http://mrdoob.com/
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
import re

import numpy

from OpenGL.GL import *
from THREE.textures.CubeTexture import *
import OpenGL.raw.GL.VERSION.GL_2_0


emptyTexture = Texture()
emptyCubeTexture = CubeTexture()

# // --- Base for inner nodes (including the root) ---


class UniformContainer():
    def __init__(self):
        self.seq = []
        self.map = {}

# // --- Utilities ---


class Uniform:
    def __init__(self, source=None):
        self.type = None
        self.value = None
        self.needsUpdate = True
        self.properties = None

        if source is None:
            return

        if isinstance(source, dict):
            if 'type' in source:
                self.type = source['type']
            self.value = source['value']
            if 'needsUpdate' in source:
                self.needsUpdate = source['needsUpdate']
        else:
            self.value = source.value
            self.properties = source.properties

    def __iter__(self):
        return iter(self.__dict__)

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        self.__dict__[key] = value


class Uniforms:
    def __init__(self, lst=None):
        if lst is None:
            return

        if isinstance(lst, Uniforms):
            lst = lst.__dict__

        for uniform in lst:
            source_uniform = lst[uniform]
            if isinstance(source_uniform, Uniform):
                # TODO FDE: is it better to get a reference of the uniform or clone the uniform ?
                new_uniform = source_uniform
            else:
                new_uniform = Uniform(source_uniform)
            self.__dict__[uniform] = new_uniform

    # def __delattr__(self, item):
    #    del self.Uniforms[item]

    # def __iter__(self):
    #    return iter(self.__dict__(keys)

    #def __getitem__(self, item):
    #    return self.__dict__[item]

    # def __setitem__(self, item, value):
    #   self.Uniforms[item] = value

# // Array Caches (provide typed arrays for temporary by size)


arrayCacheF32 = [None for i in range(32)]
arrayCacheI32 = [None for i in range(32)]

# // Float32Array caches used for uploading Matrix uniforms

mat4array = np.zeros(16, 'f' )
mat3array = np.zeros( 9 , 'f')
mat2array = np.zeros( 4, 'f' )

# // Flattening for arrays of vectors and matrices


def flatten(array, nBlocks, blockSize):
    firstElem = array[0]

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
        firstElem.toArray(r, 0)
        offset = 0
        for i in range(1, nBlocks):
            offset += blockSize
            array[i].toArray(r, offset)

    return r


def arraysEqual(a, b):
    # lb = len(b)
    # eq = (a[0:lb] == b[0:lb])
    # return eq.all()
    return np.array_equal(a, b)


def copyArray(a, b):
    #lb = len(b)
    #a[0:lb] = b[:]
    np.copyto(a, b)

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


_cache_size = {
    0x1406: 1,  # // FLOAT
    0x8b50: 2,  # // _VEC2
    0x8b51: 3,  # // _VEC3
    0x8b52: 4,  # // _VEC4

    0x8b5a: 4,  # self.setValue2fm,  # // _MAT2
    0x8b5b: 9,  # self.setValue3fm,  # // _MAT3
    0x8b5c: 16,  # self.setValue4fm,  # // _MAT4

    0x8b5e: 1,
    0x8d66: 1,  # // SAMPLER_2D, SAMPLER_EXTERNAL_OES
    0x8b60: 1,  # // SAMPLER_CUBE

    0x1404: 1,
    GL_UNSIGNED_INT: 1,
    0x8b56: 1,  # // INT, BOOL
    0x8b53: 0,  # self.setValue2iv,
    0x8b57: 0,  # self.setValue2iv,  # // _VEC2
    0x8b54: 0,  # self.setValue3iv,
    0x8b58: 0,  # self.setValue3iv,  # // _VEC3
    0x8b55: 0,  # self.setValue4iv,
    0x8b59: 0,  # self.setValue4iv  # // _VEC4
}


class SingleUniform:
    def __init__(self, id, activeInfo, addr):
        global _cache_size
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
            GL_UNSIGNED_INT: self.setValue1ui,
            0x8b56: self.setValue1i,  # // INT, BOOL
            0x8b53: self.setValue2iv,
            0x8b57: self.setValue2iv,  # // _VEC2
            0x8b54: self.setValue3iv,
            0x8b58: self.setValue3iv,  # // _VEC3
            0x8b55: self.setValue4iv,
            0x8b59: self.setValue4iv  # // _VEC4
        }
        v = _types[activeInfo[2]]
        cv = _cache_size[activeInfo[2]]

        self.id = id
        self.addr = addr
        self.uploaded = False
        self.cache = np.full(cv, -99999999999999999999999999999, np.float32)

        self.setValue = v

    # // Single scalar

    def setValue1f(self, v, renderer=None, force=False):
        cache = self.cache

        if cache[0] == v:
            return

        OpenGL.raw.GL.VERSION.GL_2_0.glUniform1f(self.addr, v)
        cache[0] = v

    def setValue1i(self, v, renderer=None, force=False):
        cache = self.cache

        if cache[0] == v:
            return

        OpenGL.raw.GL.VERSION.GL_2_0.glUniform1i(self.addr, v)
        cache[0] = v

    def setValue1ui(self, v, renderer=None, force=False):
        cache = self.cache

        if cache[0] == v:
            return

        OpenGL.raw.GL.VERSION.GL_3_0.glUniform1ui(self.addr, v)
        cache[0] = v

        # // Single float vector (from flat array or THREE.VectorN)

    def setValue2fv(self, v, renderer=None, force=False):
        cache = self.cache

        if v.x is not None:
            if cache[0] != v.x or cache[1] != v.y:
                OpenGL.raw.GL.VERSION.GL_2_0.glUniform2f(self.addr, v.x, v.y)
                cache[0] = v.x
                cache[1] = v.y
        else:
            if arraysEqual(cache, v):
                return

            OpenGL.raw.GL.VERSION.GL_2_0.glUniform2fv(self.addr, v)

            copyArray(cache, v)

    def setValue3fv(self, v, renderer=None, force=False):
        cache = self.cache

        if v.my_class(isVector3):
            vnp = v.np
            if cache[0] != vnp[0] or cache[1] != vnp[1] or cache[2] != vnp[2]:
                OpenGL.raw.GL.VERSION.GL_2_0.glUniform3f(self.addr, vnp[0], vnp[1], vnp[2])
                numpy.copyto(cache, vnp)

        elif v.my_class(isColor):
            np = v.np
            if cache[0] != np[0] or cache[1] != np[1] or cache[2] != np[2]:
                OpenGL.raw.GL.VERSION.GL_2_0.glUniform3f(self.addr, np[0], np[1], np[2])
                cache[0] = np[0]
                cache[1] = np[1]
                cache[2] = np[2]

        else:
            if arraysEqual(cache, v):
                return

            OpenGL.raw.GL.VERSION.GL_2_0.glUniform3fv(self.addr, 1, v)
            copyArray(cache, v)

    def setValue4fv(self, v, renderer=None, force=False):
        cache = self.cache

        if hasattr(v, 'x') is not None:
            if cache[0] != v.x or cache[1] != v.y or cache[2] != v.z or cache[3] != v.w:
                OpenGL.raw.GL.VERSION.GL_2_0.glUniform4f(self.addr, v.x, v.y, v.z, v.w)

            cache[0] = v.x
            cache[1] = v.y
            cache[2] = v.z
            cache[3] = v.w

        else:
            if arraysEqual(cache, v):
                return

            OpenGL.raw.GL.VERSION.GL_2_0.glUniform4fv(self.addr, v)

            copyArray(cache, v)

    # // Single matrix (from flat array or MatrixN)

    def setValue2fm(self, v, renderer=None, force=False):
        cache = self.cache

        if not hasattr(v, 'elements'):
            if arraysEqual(cache, v):
                return

            OpenGL.raw.GL.VERSION.GL_2_0.glUniformMatrix2fv(self.addr, 1, GL_FALSE, v)
            copyArray(cache, v)

        else:
            elements = v.elements
            if arraysEqual(cache, elements):
                return

            np.copyto(mat2array, elements)
            OpenGL.raw.GL.VERSION.GL_2_0.glUniformMatrix2fv(self.addr, 1, GL_FALSE, mat2array)

        copyArray(cache, elements)

    def setValue3fm(self, v, renderer=None, force=False):
        cache = self.cache

        if not hasattr(v, 'elements'):
            if arraysEqual(cache, v):
                return

            glUniformMatrix3fv(self.addr, GL_FALSE, v)
            copyArray(cache, v)

        else:
            elements = v.elements

            if not force and arraysEqual(cache, elements):
                return

            # np.copyto(mat3array, elements)

            OpenGL.raw.GL.VERSION.GL_2_0.glUniformMatrix3fv(self.addr, 1, GL_FALSE, elements)
            if not force:
                copyArray(cache, elements)

    def setValue4fm(self, v, renderer=None, force=False):
        cache = self.cache

        if not hasattr(v, 'elements'):
            if arraysEqual(cache, v):
                return

            glUniformMatrix4fv(self.addr, GL_FALSE, v)
            copyArray(cache, v)

        else:
            elements = v.elements
            if not force and arraysEqual(cache, elements):
                return

            # np.copyto(mat4array, elements)

            OpenGL.raw.GL.VERSION.GL_2_0.glUniformMatrix4fv(self.addr, 1, GL_FALSE, elements)

            if not force:
                copyArray(cache, elements)

    # // Single texture (2D / Cube)

    def setValueT1(self, v, renderer, force=False):
        cache = self.cache
        unit = renderer.allocTextureUnit()

        if cache[0] != unit:
            glUniform1i(self.addr, unit)
            cache[0] = unit

        renderer.textures.setTexture2D(v or emptyTexture, unit)

    def setValueT6(self, v, renderer, force=False):
        cache = self.cache
        unit = renderer.allocTextureUnit()

        if cache[0] != unit:
            glUniform1i(self.addr, unit)
            cache[0] = unit

        renderer.setTextureCube(v or emptyCubeTexture, unit)

    # // Integer / Boolean vectors or arrays thereof (always flat arrays)

    def setValue2iv(self, v, renderer=None, force=False):
        cache = self.cache

        if arraysEqual(cache, v):
            return

        glUniform2iv(self.addr, v)
        copyArray(cache, v)

    def setValue3iv(self, v, renderer=None, force=False):
        cache = self.cache

        if arraysEqual(cache, v):
            return

        glUniform3iv(self.addr, v)
        copyArray(cache, v)

    def setValue4iv(self, v, renderer=None, force=False):
        cache = self.cache

        if arraysEqual(cache, v):
            return

        glUniform4iv(self.addr, v)
        copyArray(cache, v)

    # // self.path = activeInfo.name; # // DEBUG


class PureArrayUniform:
    def __init__(self, id, activeInfo, addr ):
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
        cv = _cache_size[activeInfo[2]]

        self.id = id
        self.addr = addr
        self.size = activeInfo[1]
        self.cache = np.full(cv * self.size, -99999999999999999999999999999, np.float32)

        self.setValue = _types[activeInfo[2]]

    def updateCache(self, data):
        cache = self.cache

        if type(data) is 'np' and len(cache) < len(data):
            self.cache = np.zeros(len(data), np.float32)

        copyArray(cache, data)

    # // Array of scalars

    def setValue1fv(self, v, renderer=None, force=False):
        cache = self.cache

        if arraysEqual(cache, v):
            return

        glUniform1fv(self.addr, len(v), v)
        copyArray(cache, v)

    def setValue1iv(self, v, renderer=None, force=False):
        cache = self.cache

        if arraysEqual(cache, v):
            return

        glUniform1iv(self.addr, len(v), v)

        copyArray(cache, v)

    def setValue2iv(self, v, renderer=None, force=False):
        cache = self.cache

        if arraysEqual(cache, v):
            return

        glUniform2iv(self.addr, len(v), v)
        copyArray(cache, v)

    def setValue3iv(self, v, renderer=None, force=False):
        cache = self.cache

        if arraysEqual(cache, v):
            return

        glUniform3iv(self.addr, len(v), v)

    def setValue4iv(self, v, renderer=None, force=False):
        cache = self.cache

        if arraysEqual(cache, v):
            return

        glUniform4iv(self.addr, len(v), v)

    # Array of vectors(flat or from THREE classes)

    def setValueV2a(self, v, renderer=None, force=False):
        cache = self.cache
        data = flatten(v, self.size, 2)

        if arraysEqual(cache, data):
            return

        glUniform2fv(self.addr, len(v), data)
        self.updateCache(data)

    def setValueV3a(self, v, renderer=None, force=False):
        cache = self.cache
        data = flatten(v, self.size, 3)

        if arraysEqual(cache, data):
            return

        glUniform3fv(self.addr, len(v), data)

        self.updateCache(data)

    def setValueV4a(self, v, renderer=None, force=False):
        cache = self.cache
        data = flatten(v, self.size, 4)

        if arraysEqual(cache, data):
            return

        glUniform4fv(self.addr, len(v), data)

        self.updateCache(data)

    # // Array of matrices (flat or from THREE clases)

    def setValueM2a(self, v, renderer=None, force=False):
        cache = self.cache
        data = flatten(v, self.size, 4)

        if arraysEqual(cache, data):
            return

        glUniformMatrix2fv(self.addr, len(v), GL_FALSE, data)

        self.updateCache(data)

    def setValueM3a(self, v, renderer=None, force=False):
        cache = self.cache
        data = flatten(v, self.size, 9)

        if arraysEqual(cache, data):
            return

        glUniformMatrix3fv(self.addr, len(v), GL_FALSE, data)

        self.updateCache(data)

    def setValueM4a(self, v, renderer=None, force=False):
        cache = self.cache
        data = flatten(v, self.size, 16)

        if arraysEqual(cache, data):
            return

        glUniformMatrix4fv(self.addr, len(v), GL_FALSE, data)

        self.updateCache(data)

    # // Array of textures (2D / Cube)

    def setValueT1a(self, v, renderer, force=False):
        cache = self.cache
        n = len(v)

        units = allocTexUnits(renderer, n)

        if not arraysEqual(cache, units):
            glUniform1iv(self.addr, n, units)
            copyArray(cache, units)

        for i in range(n):
            renderer.setTexture2D(v[i] or emptyTexture, units[i])

    def setValueT6a(self, v, renderer, force=False):
        cache = self.cache
        n = len(v)

        units = allocTexUnits(renderer, n)

        if not arraysEqual(cache, units):
            glUniform1iv(self.addr, units)
            copyArray(cache, units)

        for i in range(n):
            renderer.setTextureCube(v[i] or emptyCubeTexture, units[i])

        # // self.path = activeInfo.name; # // DEBUG
    
    
class StructuredUniform( UniformContainer):
    def __init__(self, id ):
        self.id = id
        super().__init__(  ) # // mix-in

    def setValue(self, value, renderer):
        # // Note: Don't need an extras 'renderer' parameter, since samplers
        # // are not allowed in structured uniforms.
        seq = self.seq

        for u in seq:
            u.setValue(value[u.id], renderer)

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


def addUniform(container, uniformObject):
    container.seq.append(uniformObject)
    container.map[ uniformObject.id ] = uniformObject


def parseUniform(activeInfo, addr, container):
    path = activeInfo[0].decode("utf-8")
    pathLength = len(path)

    # // reset RegExp object, because of the early exit of a previous run
#    _RePathPart.lastindex = 0

    pattern = '([\w\d_]+)(\])?(\[|\.)?'
    for match in re.finditer(pattern, path):
        matchEnd = match.regs[0][1]

        id = match.group(1)
        idIsIndex = match.group(2) == ']'
        subscript = match.group(3)

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
                next = StructuredUniform(id)
                addUniform(container, next)
            else:
                next = map[id]

            container = next

# // Root Container


_variable_type = {
    "float": 0x1406,
    "vec2": 0x8b50,
    "vec3": 0x8b51,
    "vec4": 0x8b52,
    "mat2": 0x8b5a,
    "mat3": 0x8b5b,
    "mat4": 0x8b5c,
    "int": 0x8b56,
    "bool": 0x8b56
}


def _parseShaderForUniforms(shader, uniforms):
    """
    @author deckfln
    Parse the shader code to find "struct NAME { variable_type variable_name; }
    Then complete the uniforms array
    :param shader:
    :param uniforms:
    :return:
    """
    if "struct " not in shader:
        return

    pattern = 'struct ([\w\d_]+) \{([^}]*)\}'
    for match in re.finditer(pattern, shader):
        name = match.group(1)
        block = match.group(2)

        # first find if there is a single uniform or an array of uniform
        uniform = "uniform "+name
        if uniform not in shader:
            continue

        # now, is it a single value or an array
        isArray = False
        index = 0
        patt = 'uniform '+name+' ([\w\d_]+)\[ *(\d)+ *\]'
        match = re.search(patt, shader)
        if match:
            isArray = True
            index = int(match.group(2))
            if index == 0:
                continue
        else:
            patt = 'uniform ' + name + ' ([\w\d_]+);'
            match = re.search(patt, shader)

        var_name = match.group(1)

        b = block.replace("\n", "")
        b = b.replace("\t", "")

        attributes = b.split(";")

        attr_coded = {}
        for attr in attributes:
            if attr == '':
                continue
            (attr_type, attr_name) = attr.split(" ")
            vtype = _variable_type[attr_type]
            attr_coded[attr_name] = vtype

        if isArray:
            for i in range(index):
                for t in attr_coded:
                    path = "%s[%d].%s" % (var_name, i, t)
                    uniforms[path] = (path.encode("utf-8"), -1, attr_coded[t])
        else:
            for t in attr_coded:
                path = "%s.%s" % (var_name, t)
                uniforms[path] = (path.encode("utf-8"), -1, attr_coded[t])


class pyOpenGLUniforms( UniformContainer ):
    def __init__( self, program, renderer, vertex, fragment ):
        super().__init__()

        self.renderer = renderer

        # unlike webGL, glGetProgramiv doesn't list structured uniform
        # thus, needs to parse the source shader to find this structures
        n = glGetProgramiv( program, GL_ACTIVE_UNIFORMS )

        for i in range(n):
            info = glGetActiveUniform(program, i)
            addr = glGetUniformLocation(program, info[0])
            if addr >= 0:
                parseUniform( info, addr, self )

        uniforms = {}
        _parseShaderForUniforms(vertex, uniforms)
        _parseShaderForUniforms(fragment, uniforms)

        for name in uniforms:
            addr = glGetUniformLocation(program, name)
            if addr >= 0:
                parseUniform(uniforms[name], addr, self)

    def setValue(self, name, value, force=False):
        if name in self.map:
            u = self.map[ name ]

            u.setValue(value, self.renderer, force)
            u.uploaded = True

    def setOptional(self, object, name ):
        if hasattr(object, name):
            v = object.__dict__[ name ]
            self.setValue( name, v )

# // Static interface

    def upload(self, seq, values, renderer):
        for u in seq:
            v = values.__dict__[u.id]

            if v.needsUpdate:
                # // note: always updating when .needsUpdate is undefined
                u.setValue(v.value, renderer)

    def seqWithValue(seq, values):
        r = []

        for u in seq:
            if u.id in values.__dict__:
                r.append( u )

        return r

