"""Distribution to pipy"""

from setuptools import setup, find_packages

with open("readme.rst") as readme:
    long_description = readme.read()

setup(
    name='neuron_poker',
    version='1.0.0',
    long_description=long_description,
    url='https://github.com/dickreuter/neuron_poker',
    author='Nicolas Dickreuter',
    author_email='dickreuter@gmail.com',
    license='MIT',
    description=('OpenAi gym for textas holdem poker with graphical rendering and montecarlo.'),
    packages=find_packages(exclude=['tests', 'gym_env', 'tools']),
    install_requires=['pyglet', 'pytest', 'pandas', 'pylint', 'gym', 'numpy', 'matplotlib'],
    platforms='any',
)
