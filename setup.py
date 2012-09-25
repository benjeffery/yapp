from distutils.core import setup

setup(
    name='yapp',
    version='0.1.0',
    author='Ben Jeffery',
    author_email='ben.jeffery@well.ox.ac.uk',
    packages=['yapp',],
    scripts=['scripts/yapp'],
    license='TODO', #TODO
    long_description=open('README.md').read(),
    install_requires=['pyyaml',]
)