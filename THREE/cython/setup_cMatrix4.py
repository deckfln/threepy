from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

setup(
    ext_modules = [
        Extension("cMatrix4",
                  sources=["cMatrix4.pyx"],
                extra_compile_args=["/fp:fast", "/favor:INTEL64"],
                include_dirs=[numpy.get_include()]
                  )
    ],
    cmdclass={"build_ext": build_ext}
)