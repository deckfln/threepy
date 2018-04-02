from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

setup(
    ext_modules = [
        Extension("cInterpolant",
                  sources=["cInterpolant.pyx"],
                extra_compile_args=["/openmp"],
                include_dirs=[numpy.get_include()]
                  )
    ],
    cmdclass={"build_ext": build_ext}
)
