from setuptools import setup, find_packages

with open("README.md", "r") as fh: 
    description = fh.read() 

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

setup( 
    name="thorr", 
    version="dev-0.0.1", 
    # author="gdarkwah", 
    # author_email="gdarkwah@uw.edu", 
    # packages=[], 
    description="A package for THORR", 
    long_description=description, 
    long_description_content_type="text/markdown", 
    url="https://github.com/UW-SASWE/THORR", 
    # license='', #TODO: add license
    python_requires='>=3.11', 
    install_requires=install_requires
) 