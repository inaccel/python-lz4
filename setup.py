#!/usr/bin/env python


from setuptools import setup, find_packages, Extension
import subprocess
import os
from distutils import ccompiler

def version_scheme(version):
    from setuptools_scm.version import guess_next_dev_version
    version = guess_next_dev_version(version)
    return version.lstrip("v")

LZ4_VERSION = "r131"

def library_is_installed(libname):
    # Check to see if we have a library called'libname' installed on the
    # system. This uses pkg-config to check for existence of the library, and
    # returns True if it's found, False otherwise. If pkg-config isn't found,
    # Flase is returned.
    try:
        pkg_config_exe = os.environ.get('PKG_CONFIG', None) or 'pkg-config'
        cmd = '{0} --exists {1}'.format(pkg_config_exe, libname).split()
        return subprocess.call(cmd) == 0
    except OSError:
        # pkg-config not present
        return False

# Check to see if we have a lz4 library installed on the system and
# use it if so. If not, we'll use the bundled library.
liblz4_found = library_is_installed('liblz4')

# Check to see if we have the py3c headers installed on the system and
# use it if so. If not, we'll use the bundled library.
py3c_found = library_is_installed('py3c')

include_dirs = []

if liblz4_found is False:
    include_dirs.append('lz4libs')

if py3c_found is False:
    include_dirs.append('py3c')

if liblz4_found:
    # Use system lz4, and don't set optimization and warning flags for
    # the compiler. Specifically we don't define LZ4_VERSION since the
    # system lz4 library could be updated (that's the point of a
    # shared library).
    if ccompiler.get_default_compiler() == "msvc":
        extra_compile_args = ["/Ot", "/Wall"]
    else:
        extra_compile_args = ["-std=c99",]

    lz4block = Extension('lz4.block._block',
                         [
                             'lz4/block/_block.c'
                         ],
                         extra_compile_args=extra_compile_args,
                         libraries=['lz4'],
                         include_dirs=include_dirs,
    )
    lz4frame = Extension('lz4.frame._frame',
                         [
                             'lz4/frame/_frame.c',
                         ],
                         extra_compile_args=extra_compile_args,
                         libraries=['lz4'],
                         include_dirs=include_dirs,
    )
else:
    # Use the bundled lz4 libs, and set the compiler flags as they
    # historically have been set. We do set LZ4_VERSION here, since it
    # won't change after compilation.
    if ccompiler.get_default_compiler() == "msvc":
        extra_compile_args = ["/Ot", "/Wall"]
    else:
        extra_compile_args = ["-std=c99","-O3","-Wall","-W","-Wundef"]

    lz4block = Extension('lz4.block._block',
                         [
                             'lz4libs/lz4.c',
                             'lz4libs/lz4hc.c',
                             'lz4/block/_block.c'
                         ],
                         extra_compile_args=extra_compile_args,
                         include_dirs=include_dirs,
    )
    lz4frame = Extension('lz4.frame._frame',
                         [
                             'lz4libs/lz4.c',
                             'lz4libs/lz4hc.c',
                             'lz4libs/lz4frame.c',
                             'lz4libs/xxhash.c',
                             'lz4/frame/_frame.c',
                         ],
                         extra_compile_args=extra_compile_args,
                         include_dirs=include_dirs,
    )
    with open('lz4/lz4version.py', 'w+') as f:
        f.write('# File autogenerated during install.\n')
        f.write('# Do not change. Do not store in version control.\n')
        f.write('LZ4_VERSION = \'' + LZ4_VERSION + '\'\n')

setup(
    name='lz4',
    use_scm_version={
        'write_to': "lz4/version.py",
        'version_scheme': version_scheme,
    },
    setup_requires=['setuptools_scm'],
    description="LZ4 Bindings for Python",
    long_description=open('README.rst', 'r').read(),
    author='Steeve Morin',
    author_email='steeve.morin@gmail.com',
    url='https://github.com/python-lz4/python-lz4',
    packages=find_packages(),
    ext_modules=[lz4block, lz4frame],
    tests_require=["nose>=1.0"],
    test_suite = "nose.collector",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
