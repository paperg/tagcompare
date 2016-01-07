import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex

        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


setup(
    name='tagcompare',
    version='0.1.1',
    description='Capture and compare creative tags!',
    url='https://github.com/paperg/tagcompare',
    packages=['tagcompare', 'tagcompare.test'],
    entry_points={
        'console_scripts': [
            'tagcapture = tagcompare.capture:main',
            'tagcompare = tagcompare.main:main',
        ]
    },
    install_requires=[
        'selenium',
        'requests',
        'pillow',
        'enum34'
    ],
    package_data={
        '': ['*.json'],
    },
    tests_require=['tox'],
    cmdclass={'test': Tox}
)
