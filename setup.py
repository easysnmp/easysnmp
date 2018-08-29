import os
import sys
import shlex
import platform
from setuptools import setup, Extension
from setuptools.command.test import test as TestCommand


def local_drive():
    return os.path.splitdrive(os.getcwd())[0] + "\\"


def get_default_snmp_path(sub_directory=None):
    drive = local_drive()
    netsnmppath = os.path.join(drive, 'usr')
    if sub_directory:
        netsnmppath = os.path.join(netsnmppath, sub_directory)
    return netsnmppath


def get_default_vcpython_path(sub_directory=None):
    localappdata = os.getenv("LOCALAPPDATA")
    vcpythonpath = os.path.join(localappdata, "Programs", "Common", "Microsoft", "Visual C++ for Python", "9.0")
    if sub_directory:
        vcpythonpath = os.path.join(vcpythonpath, sub_directory)
    return vcpythonpath


def get_default_vc_path(sub_directory=None):
    vcpath = get_default_vcpython_path(sub_directory="VC")
    if sub_directory:
        vcpath = os.path.join(vcpath, sub_directory)
    return vcpath


def get_default_winsdk_path(sub_directory=None):
    vcpath = get_default_vcpython_path(sub_directory="WinSDK")
    if sub_directory:
        vcpath = os.path.join(vcpath, sub_directory)
    return vcpath


def handle_netsnmp():
    print("On Windows, looking for net-snmp installation...")
    installed_netsnmp = os.path.join(get_default_snmp_path(sub_directory="bin"), "netsnmp.dll")
    if not os.path.isfile(installed_netsnmp):
        netsnmp_exe = "net-snmp-5.7.0-1.x86.exe"
        print("Net-SNMP doesn't appear to be installed. Running installer...")
        netsnmp_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), netsnmp_exe)
        # Flags:
        # /StartMenu={GroupName}
        # /Agent=standard|extDLL|none
        # /noTrapd (default \Trapd)
        # /noPerl (default \Perl)
        # /Dev (default \noDev)
        # /OpenSSL (default \noOpenSSL)
        os.system('"{}" /Dev /OpenSSL /S /Q'.format(netsnmp_path))
        print("Net-SNMP installed.")


def handle_vc(vcpath):
    print("Looking for C++ build tools")
    if not os.path.isfile(vcpath):
        print("C++ Build Tools MISSING!!!!!!")
        print("Installing build tools")
        msi_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "VCForPython27.msi")
        os.system('msiexec /i {} ALLUSERS=1 /qn'.format(msi_path))
        print("C++ Build Tools installed")
    if os.path.isfile(vcpath):
        import distutils.msvc9compiler
        old_find = distutils.msvc9compiler.find_vcvarsall

        def new_find(version):
            try:
                return vcpath
            except:
                path = old_find(version)
                return path

        distutils.msvc9compiler.find_vcvarsall = new_find


if platform.system() == 'Windows':
    os.environ["DISTUTILS_USE_SDK"] = "1"
    os.environ["MSSdk"] = "1"

    vc_python_path = get_default_vcpython_path()
    vc_vars_path = os.path.join(vc_python_path, "vcvarsall.bat")

    handle_netsnmp()
    handle_vc(vc_vars_path)

    cl_exe = get_default_vc_path(sub_directory="bin")
    os.environ["PATH"] += ";" + cl_exe

    vc_include = get_default_vc_path(sub_directory="include")
    vc_lib = get_default_vc_path(sub_directory="lib")

    winsdk_lib = get_default_winsdk_path(sub_directory="lib")
    winsdk_include = get_default_winsdk_path(sub_directory="include")

    netsnmp_include = get_default_snmp_path(sub_directory="include")
    netsnmp_lib = get_default_snmp_path(sub_directory="lib")

    netsnmp_dll = os.path.join(get_default_snmp_path(sub_directory="bin"), "netsnmp.dll")
    msvrc90_dll = os.path.join(get_default_snmp_path(sub_directory="bin"), "msvcr90.dll")

    compile_args = ["/MD", "/O2", "/Zi", "/W3", "/WX-", "/Oy-", "/DWIN32", "/D_WINDOWS", "/D_USRDLL",
                    "/DEASYSNMP_EXPORTS", "/D_WINDLL", "/Gm-", "/EHsc", "/GS", "/TC"]

    incdirs = [netsnmp_include, vc_include, winsdk_include]
    libdirs = [netsnmp_lib, winsdk_lib, vc_lib]
    libs = ["python27", "Ws2_32", "netsnmp"]
    data_files = [(sys.exec_prefix + "\\dlls", [netsnmp_dll, msvrc90_dll])]
    sources = ['easysnmp/interface_windows.c']
    zip_safe = False

else:
    # Determine if a base directory has been provided with the --basedir option
    basedir = None
    in_tree = False
    # Add compiler flags if debug is set
    compile_args = []
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

        libdirs = os.popen('{0}/net-snmp-config --build-lib-dirs {1}'.format(basedir, basedir)).read()  # noqa
        incdirs = os.popen('{0}/net-snmp-config --build-includes {1}'.format(basedir, basedir)).read()  # noqa

        libs = [flag[2:] for flag in shlex.split(netsnmp_libs) if flag.startswith('-l')]  # noqa
        libdirs = [flag[2:] for flag in shlex.split(libdirs) if flag.startswith('-L')]  # noqa
        incdirs = [flag[2:] for flag in shlex.split(incdirs) if flag.startswith('-I')]  # noqa

    # Otherwise, we use the system-installed SNMP libraries
    else:
        netsnmp_libs = os.popen('net-snmp-config --libs').read()

        libs = [flag[2:] for flag in shlex.split(netsnmp_libs) if flag.startswith('-l')]  # noqa
        libdirs = [flag[2:] for flag in shlex.split(netsnmp_libs) if flag.startswith('-L')]  # noqa
        incdirs = []

        if sys.platform == 'darwin':  # OS X
            brew = os.popen('brew info net-snmp').read()
            if 'command not found' not in brew and 'error' not in brew:
                # /usr/local/opt is the default brew `opt` prefix, however the user
                # may have installed it elsewhere. The `brew info <pkg>` includes
                # an apostrophe, which breaks shlex. We'll simply replace it
                libdirs = [flag[2:] for flag in shlex.split(brew.replace('\'', '')) if flag.startswith('-L')]  # noqa
                incdirs = [flag[2:] for flag in shlex.split(brew.replace('\'', '')) if flag.startswith('-I')]  # noqa
                # The homebrew version also depends on the Openssl keg
                brew = os.popen('brew info openssl').read()
                libdirs += [flag[2:] for flag in shlex.split(brew.replace('\'', '')) if flag.startswith('-L')]  # noqa
                incdirs += [flag[2:] for flag in shlex.split(brew.replace('\'', '')) if flag.startswith('-I')]  # noqa
    sources = ['easysnmp/interface.c']
    data_files = {}
    zip_safe = True


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


# Read the long description from README.rst
with open('README.rst') as f:
    long_description = f.read()

setup(
    name='easysnmp',
    version='0.2.5',
    description='A blazingly fast and Pythonic SNMP library based on the '
                'official Net-SNMP bindings',
    long_description=long_description,
    author='Kent Coble',
    author_email='coblekent@gmail.com',
    url='https://github.com/kamakazikamikaze/easysnmp',
    license='BSD',
    packages=['easysnmp'],
    tests_require=['pytest-cov', 'pytest-flake8', 'pytest-sugar', 'pytest'],
    cmdclass={'test': PyTest},
    data_files=data_files,
    zip_safe=zip_safe,
    ext_modules=[
        Extension(
            'easysnmp.interface', sources,
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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring'
    ]
)
