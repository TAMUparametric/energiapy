from setuptools import setup, find_packages
from pathlib import Path

__version__ = "1.0.2"

short_desc = (
    "Python-based energy systems modeling and optimization tool"
)

# with open('README.md') as file:
#     long_description = file.read()
this_directory = Path(__file__).parent
long_description = (this_directory/'README.md').read_text()
    
setup(
    name='energiapy',
    version=__version__,
    author='Rahul Kakodkar',
    author_email='cacodcar@tamu.edu',
    description=short_desc,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url='https://github.com/TAMUparametric/energiapy',
    install_requires=[
        'numpy',
        'pandas',
        'pyomo',
        'h5pyd',
        'scipy',
        'matplotlib',
        'scikit-learn',
        'openpyxl',
        'ppopt',
        'gurobipy',
    ],
    packages=find_packages(where='src'),
    package_dir={'': 'src'}
)
