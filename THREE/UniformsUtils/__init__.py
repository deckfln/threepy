"""
/**
 * Uniform Utilities
 */
"""
from THREE.Javascript import *
from THREE.renderers.pyOpenGL.pyOpenGLUniforms import *


def merge( uniforms ):
        merged = {}

        for u in uniforms:
            tmp = clone( u)

            for p in tmp:
                merged[ p ] = tmp[ p ]

        return Uniforms(merged)


def clone( uniforms_src ):
        if isinstance(uniforms_src, dict):
            uniforms_dst = {}
            src = uniforms_src
            dst = uniforms_dst
        else:
            uniforms_dst = type(uniforms_src)()
            src = uniforms_src.__dict__
            dst = uniforms_dst.__dict__

        for u in src:
            dst[ u ] = Uniform()

            su = src[ u ]
            keys = su.__dict__

            for p in keys:
                parameter_src = su.__dict__[ p ]

                if isinstance(parameter_src, int) or isinstance(parameter_src, float):
                    dst[ u ].__dict__[ p ] = parameter_src
                elif isinstance(parameter_src, dict):
                    dst[ u ].__dict__[ p ] = parameter_src
                elif isinstance(parameter_src, list):
                    dst[u].__dict__[p] = parameter_src[:]
                elif isinstance(parameter_src, javascriptObject):
                    dst[ u ].__dict__[ p ] = parameter_src
                elif isinstance(parameter_src, str):
                    dst[u].__dict__[p] = parameter_src
                elif parameter_src is not None and (
                        parameter_src.my_class(isColor) or
                        parameter_src.my_class(isMatrix3) or parameter_src.my_class(isMatrix4) or
                        parameter_src.my_class(isVector2) or parameter_src.my_class(isVector3) or parameter_src.my_class(isVector4) or
                        parameter_src.my_class(isTexture)):
                        dst[ u ].__dict__[ p ] = parameter_src.clone()
                else:
                    dst[ u ].__dict__[ p ] = parameter_src

        return uniforms_dst
