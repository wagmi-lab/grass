import pathlib
from setuptools import find_packages, setup

with open('"./requirements.txt"', 'r') as f:
    install_reqs = [
        s for s in [
            line.split('#', 1)[0].strip(' \t\n') for line in f
        ] if s != ''
    ]

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# This call to setup() does all the work
setup(
    name='grass-fork',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_reqs,
    author='Quant',
    classifiers=[],
    entry_points={
        "console_scripts": []  
    }
)
