from distutils.core import setup

setup(
    name='pyneslab',
    version='0.1',
    packages=['pyneslab'],
    install_requires=['pyserial'],
    scripts=['scripts/chiller-control'],
    url='https://github.com/wschoenell/pyneslab',
    license='BSD',
    author='William Schoenell',
    author_email='wschoenell@gmail.com',
    description='Python module for NESLAB Thermo Scientific chiller control'
)
