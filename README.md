# EarthML - Geodata to Geohash
![earthml Logo](https://github.com/akhilchibber/earthml/blob/main/earthml_logo.png?raw=true)
<p align="center">
  <img src="https://github.com/akhilchibber/earthml/blob/main/earthml_logo.png?raw=true" width="200" alt="earthml Logo">
</p>

EarthML is a Python library designed to convert geospatial datasets into a single geohash representing the smallest possible area that covers the entire dataset. It supports various formats, including `.shp`, `.geojson`, `.tif`, `.las`, `.png`, `.jpg`, and `.jpeg`.

## Goal

The goal of EarthML is to simplify the process of converting geospatial data into a geohash. It can handle different file formats and automatically calculate the geohash that fits the entire study area.

## Features

- **Support for Multiple Formats**: Easily convert geospatial data in Shapefile, GeoJSON, GeoTIFF, LAS, and image formats.
- **Geohash Calculation**: Automatically calculates the geohash that best represents the geographical bounds of the dataset.
- **Easy to Use**: Intuitive functions for loading and processing geospatial data.

## Installation

To install EarthML, you can use pip:

```
pip install earthml
```





# Usage

```
from earthml import geodata_to_geohash

# Calculate geohash
geohash = geodata_to_geohash.find_smallest_geohash('file1.shp')
```





# License
This project is licensed under the MIT License. See the LICENSE file for details.





# Author
Akhil Chhibber






# Note
This README provides a brief overview of the library, explains its goal, highlights key features, and provides simple installation and usage instructions.
