import os
import re
import sys

from setuptools import setup, Extension
from setuptools.command.test import test as TestCommand

# Determine if a base directory has been provided with the --basedir option
in_tree = False
for arg in sys.argv:
    if arg.startswith('--basedir='):
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

    libs = re.findall(r" -l(\S+)", netsnmp_libs)
    libdirs = re.findall(r" -L(\S+)", libdir)
    incdirs = re.findall(r" -I(\S+)", incdir)

# Otherwise, we use the system-installed SNMP libraries
else:
    netsnmp_libs = os.popen('net-snmp-config --libs').read()

    libs = re.findall(r" -l(\S+)", netsnmp_libs)
    libdirs = re.findall(r" -L(\S+)", netsnmp_libs)
    incdirs = []


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

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


setup(
    name="easysnmp",
    version="1.0",
    description='A more Pythonic Net-SNMP Python Interface',
    author='Fotis Gimian',
    author_email='fgimiansoftware@gmail.com',
    url='https://github.com/fgimian/easysnmp',
    license="BSD",
    packages=['easysnmp'],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    ext_modules=[
        Extension(
            "easysnmp.interface", ["easysnmp/interface.c"],
            library_dirs=libdirs, include_dirs=incdirs, libraries=libs
        )
    ]
)
