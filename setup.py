from setuptools import setup, find_packages
import os
__version__ = "1.0.4"

short_desc = (
    "Python-based energy systems modeling and optimization tool"
)

def setup_package():
    with open('README.md', encoding='utf-8') as f:
            long_description = f.read()
        
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
        extras_require={
            'test': ['pytest'],
        },
        packages=find_packages(where='src'),
        package_dir={'': 'src'},
    )
    
if __name__ == '__main__':
    setup_package()