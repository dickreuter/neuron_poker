"""Setup py distutils"""

# pylint: skip-file

from distutils.core import setup

from Cython.Build import cythonize

setup(name='montecarlo_cython',
      ext_modules=cythonize("montecarlo_cython.pyx"))
