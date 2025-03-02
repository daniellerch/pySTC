import os, sys
from setuptools import setup, Extension, find_packages


if sys.platform == "win32":
    extra_compile_args = ["/std:c++11"]
    extra_link_args = []
elif sys.platform == "darwin":
    extra_compile_args = ["-std=c++11", "-stdlib=libc++"]
    extra_link_args = []
else:
    extra_compile_args = ["-std=c++11", "-Wno-narrowing"]
    extra_link_args = []

stc_extension = Extension(
    'pystc.stc_extension', 
    include_dirs = ['pystc/'],
    sources = ['pystc/common.cpp',
               'pystc/stc_embed_c.cpp',
               'pystc/stc_extract_c.cpp',
               'pystc/stc_interface.cpp',
               'pystc/stc_ml_c.cpp'],
    extra_compile_args = extra_compile_args,
    extra_link_args = extra_link_args,
    language='c++',
)


setup(name = 'PySTC',
      version = '0.1',
      author="Daniel Lerch Hostalot",
      author_email="dlerch@gmail.com",
      url="https://github.com/daniellerch/pySTC",
      description = 'A Python interface for Syndrome Trellis Codes Steganography',
      packages=find_packages(),
      ext_modules = [stc_extension])


