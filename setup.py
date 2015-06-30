import os
import re
import sys

from setuptools import setup, Extension
from setuptools.command.test import test as TestCommand

# Determine if a base directory has been provided with the --basedir option
in_tree = False
# Add compiler flags if debug is set
compile_args = ['-Wno-unused-function']
for arg in sys.argv:
    if arg.startswith('--debug'):
        # Note from GCC manual:
        #       If you use multiple -O options, with or without level numbers,
        #       the last such option is the one that is effective.
        compile_args.extend('-Wall -O0 -g'.split())
    elif arg.startswith('--basedir='):
        basedir = arg.split('=')[1]
        sys.argv.remove(arg)
        in_tree = True

# If a base directory has been provided, we use it
if in_tree:
    netsnmp_libs = os.popen(basedir + '/net-snmp-config --libs').read()

    libdir = os.popen(
        basedir + '/net-snmp-config --build-lib-dirs ' + basedir).read()
    incdir = os.popen(
        basedir + '/net-snmp-config --build-includes ' + basedir).read()

    libs = re.findall(r' -l(\S+)', netsnmp_libs)
    libdirs = re.findall(r' -L(\S+)', libdir)
    incdirs = re.findall(r' -I(\S+)', incdir)

# Otherwise, we use the system-installed SNMP libraries
else:
    netsnmp_libs = os.popen('net-snmp-config --libs').read()

    libs = re.findall(r' -l(\S+)', netsnmp_libs)
    libdirs = re.findall(r' -L(\S+)', netsnmp_libs)
    incdirs = []


# Setup the py.test class for use with the test command
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


# Read the long description from readme.rst
try:
    with open('setup.rst') as f:
        long_description = f.read()
except IOError:
    long_description = None


setup(
    name='easysnmp',
    version='0.2.3',
    description='A blazingly fast and Pythonic SNMP library based on the '
                'official Net-SNMP bindings',
    long_description=long_description,
    author='Fotis Gimian',
    author_email='fgimiansoftware@gmail.com',
    url='https://github.com/fgimian/easysnmp',
    license='BSD',
    packages=['easysnmp'],
    tests_require=['pytest-cov', 'pytest-flake8', 'pytest-sugar', 'pytest'],
    cmdclass={'test': PyTest},
    ext_modules=[
        Extension(
            'easysnmp.interface', ['easysnmp/interface.c'],
            library_dirs=libdirs, include_dirs=incdirs, libraries=libs,
            extra_compile_args=compile_args
        )
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring'
    ]
)
