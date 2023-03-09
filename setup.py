from setuptools import setup, find_packages

__version__ = "1.0.0"

short_desc = (
    "Python-based energy systems modeling and optimization tool"
)

with open('README.md') as f:
    long_description = f.read()

setup(
    name='energiapy',
    version=__version__,
    author='Rahul Kakodkar',
    author_email='cacodcar@tamu.edu',
    description=short_desc,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='',
    url='',
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
        'setuptools'
    ],
    packages=find_packages(where='src'),
    package_dir={'': 'src'}
)

