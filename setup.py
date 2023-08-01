from setuptools import setup, find_packages

# Read the content of the README.md file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='earthml',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'fiona',
        'rasterio',
        'pygeohash',
        'Pillow',
        'laspy',
    ],
    author='Akhil Chhibber',
    author_email='akhil.chibber@gmail.com',
    description='A library to Perform different possible operations on Geo-Spatial Dataset',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/akhilchibber',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)