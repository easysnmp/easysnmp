from setuptools import setup, Extension
import os
import re
import sys

# Determine if a base directory has been provided with the --basedir option
intree = False
for arg in sys.argv:
    if arg.startswith('--basedir='):
        basedir = arg.split('=')[1]
        sys.argv.remove(arg)
        intree = True

# If a base directory has been provided, we use it
if intree:
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


setup(
    name="PyNetSNMP",
    version="1.0",
    description='A more Pythonic Net-SNMP Python Interface',
    author='Fotis Gimian',
    author_email='fgimiansoftware@gmail.com',
    url='https://github.com/fgimian/PyNetSNMP',
    license="BSD",
    packages=['pynetsnmp'],

    # TODO: Update this to use py.test and our new test suite
    # test_suite="netsnmp.tests.test",

    ext_modules=[
        Extension(
            "pynetsnmp.client_intf", ["pynetsnmp/client_intf.c"],
            library_dirs=libdirs, include_dirs=incdirs, libraries=libs
        )
    ]
)
