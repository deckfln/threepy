"""
/**
 * Uniform Utilities
 */
"""


def merge( uniforms ):
        merged = {}

        for u in range(len(uniforms)):
            tmp = clone( uniforms[ u ] )

            for p in tmp:
                merged[ p ] = tmp[ p ]

        return merged


def clone( uniforms_src ):
        if isinstance(uniforms_src, dict):
            uniforms_dst = {}
        else:
            uniforms_dst = type(uniforms_src)()

        for u in uniforms_src:
            uniforms_dst[ u ] = {}

            for p in uniforms_src[ u ]:
                parameter_src = uniforms_src[ u ][ p ]

                if isinstance(parameter_src, int) or isinstance(parameter_src, float):
                    uniforms_dst[ u ][ p ] = parameter_src
                elif isinstance(parameter_src, dict):
                    uniforms_dst[ u ][ p ] = parameter_src
                elif parameter_src and ( parameter_src.isColor or
                    parameter_src.isMatrix3 or parameter_src.isMatrix4 or
                    parameter_src.isVector2 or parameter_src.isVector3 or parameter_src.isVector4 or
                    parameter_src.isTexture):
                    uniforms_dst[ u ][ p ] = parameter_src.clone()

                elif isinstance(parameter_src, list):
                    uniforms_dst[ u ][ p ] = parameter_src[:]
                else:
                    uniforms_dst[ u ][ p ] = parameter_src

        return uniforms_dst
