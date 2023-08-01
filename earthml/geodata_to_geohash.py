'''
THE GOAL OF THIS PYTHON SCRIPT IS TO FIND THE SMALLEST POSSIBLE SINGLE GEOHASH THAT COVERS THE AREA OF A GIVEN
GEOSPATIAL DATASET IN DIFFERENT FORMATS INCLUDING .shp, .geojson, .tif, .las, .png, .jpg, and .jpeg!
'''





# IMPORTING THE ESSENTIAL LIBRARIES
import os
import fiona
import rasterio
import pygeohash as gh
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import laspy





# FUNCTION 1: TO GET FILE EXTENSION
def get_file_extension(file):
    """
        Extracts the file extension from a file name.

        Args:
            file (str): The file name.

        Returns:
            str: The file extension.
    """
    return os.path.splitext(file)[1]





# FUNCTION 2: TO READ A GEOTIFF FILE
def open_tiff_file(tiff_file):
    """
        Opens a GeoTIFF file.

        Args:
            tiff_file (str): The name of the GeoTIFF file.

        Returns:
            rasterio.io.DatasetReader: A file object representing the opened GeoTIFF file.
    """
    return rasterio.open(tiff_file)





# FUNCTION 3: TO READ A SHAPEFILE OR GEOJSON FILE
def open_vector_file(vector_file):
    """
        Opens a vector file.

        Args:
            vector_file (str): The name of the vector file.

        Returns:
            geopandas.geodataframe.GeoDataFrame: A GeoDataFrame object representing the opened vector file.
    """
    return fiona.open(vector_file, 'r')





# FUNCTION 4: TO READ A POINT CLOUD FILE
def open_las_file(las_file):
    """
    Opens a LAS file.

    Args:
        las_file (str): The name of the LAS file.

    Returns:
        laspy.LasData.LasData: A file object representing the opened LAS file.
    """
    return laspy.read(las_file)





# FUNCTION 5: TO OPEN A .FGB FILE
def open_fgb_file(fgb_file):
    """
        Opens a FlatGeobuf file.

        Args:
            fgb_file (str): The name of the FlatGeobuf file.

        Returns:
            geopandas.geodataframe.GeoDataFrame: A GeoDataFrame object representing the opened FlatGeobuf file.
    """
    return fiona.open(fgb_file, 'r')





# FUNCTION 6: TO GET BOUNDS OF A GEOTIFF FILE
def load_tiff_bounds(tiff_file):
    """
        Get the geographical bounds of a GeoTIFF file.

        Args:
            tiff_file (str): The name of the GeoTIFF file.

        Returns:
            tuple: A tuple of four values representing the geographical bounds of the data in the file.
    """
    with open_tiff_file(tiff_file) as src:
        bounds = src.bounds
    return bounds





# FUNCTION 7: TO GET BOUNDS OF A SHAPEFILE OR GEOJSON FILE
def load_vector_bounds(vector_file):
    """
        Get the geographical bounds of a vector file.

        Args:
            vector_file (str): The name of the vector file.

        Returns:
            tuple: A tuple of four values representing the geographical bounds of the data in the file.
    """
    with open_vector_file(vector_file) as src:
        bounds = src.bounds
    return bounds





# FUNCTION 8: TO GET BOUNDS OF POINT CLOUD FILE
def load_las_bounds(las_file):
    """
    Get the geographical bounds of a LAS file.

    Args:
        las_file (str): The name of the LAS file.

    Returns:
        tuple: A tuple of four values representing the 2D geographical bounds of the data in the file.
    """
    src = open_las_file(las_file)
    min_x, min_y, _ = src.header.min
    max_x, max_y, _ = src.header.max
    return min_x, min_y, max_x, max_y





# FUNCTION 9: TO GET BOUNDS OF A .FGB FILE
def load_fgb_bounds(fgb_file):
    """
        Get the geographical bounds of a FlatGeobuf file.

        Args:
            fgb_file (str): The name of the FlatGeobuf file.

        Returns:
            tuple: A tuple of four values representing the geographical bounds of the data in the file.
    """
    with open_fgb_file(fgb_file) as src:
        minx, miny, maxx, maxy = float('inf'), float('inf'), float('-inf'), float('-inf')
        for feature in src:
            bounds = feature['geometry']['coordinates']
            for polygon in bounds:
                for coords in polygon:
                    for coord in coords:
                        x, y = coord
                        minx = min(minx, x)
                        maxx = max(maxx, x)
                        miny = min(miny, y)
                        maxy = max(maxy, y)
    return minx, miny, maxx, maxy





# FUNCTION 10: TO EXTRACT LATITUDE AND LONGITUDE FROM AN IMAGE
def get_image_bounds(image_file):
    """
        Extracts the geographical bounds from an image file.

        Args:
            image_file (str): The name of the image file.

        Returns:
            tuple: A tuple of four values representing the geographical bounds of the image,
                   or None if the image does not have geolocation data.
    """
    img = Image.open(image_file)
    geotags = get_geotagging(img)
    if geotags is None:
        return None  # No geolocation data found

    lat, lon = get_coordinates(geotags)
    return (lon, lat, lon, lat)





# FUNCTION 11: TO GET GEOTAGGING
def get_geotagging(img):
    """
        Extracts geotagging information from an image.

        Args:
            img (PIL.PngImagePlugin.PngImageFile): An image file.

        Returns:
            dict or None: A dictionary containing the geotagging data, or None if no geotagging data can be found.
    """
    exif = img._getexif()
    if not exif:
        return None  # No EXIF metadata found

    geotagging = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif:
                return None  # No EXIF geotagging found

            for (t, value) in GPSTAGS.items():
                if t in exif[idx]:
                    geotagging[value] = exif[idx][t]

    return geotagging






# FUNCTION 12: TO GET DECIMAL FROM DMS
def get_decimal_from_dms(dms, ref):
    """
        Converts geographical coordinates from degrees, minutes, and seconds to decimal degrees.

        Args:
            dms (tuple): A tuple representing a coordinate in DMS format (degrees, minutes, seconds).
            ref (str): A reference indicating the hemisphere.

        Returns:
            float: The coordinate in decimal degrees.
    """
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)





# FUNCTION 13: TO GET COORDINATES
def get_coordinates(geotags):
    """
        Extracts latitude and longitude from geotagging data.

        Args:
            geotags (dict): A dictionary of geotagging data.

        Returns:
            tuple: A tuple of two values: latitude and longitude in decimal degrees.
    """
    lat = get_decimal_from_dms(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])
    lon = get_decimal_from_dms(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])
    return (lat,lon)





# FUNCTION 14: TO IDENTIFY THE EXTREMES FOR MULTIPLE FILES
def load_and_calculate_union_bounds(files):
    """
        Calculates the smallest bounding box that includes all points in the given files.

        Args:
            files (list of str): A list of file names.

        Returns:
            tuple or None: A tuple of four values representing the geographical bounds of the data in the files,
                           or None if no geolocation data is found in any of the files.
    """
    minx, miny, maxx, maxy = [], [], [], []
    no_geolocation_data = False
    for file in files:
        extension = get_file_extension(file)
        if extension in ['.shp', '.geojson']:
            bounds = load_vector_bounds(file)
        elif extension == '.tif':
            bounds = load_tiff_bounds(file)
        elif extension == '.fgb':
            bounds = load_fgb_bounds(file)
        elif extension == '.las':
            bounds = load_las_bounds(file)
        elif extension in ['.png', '.jpeg', '.jpg']:
            bounds = get_image_bounds(file)
            if bounds is None:  # No geolocation data found
                print(f"No geolocation data found in {file}")
                no_geolocation_data = True
                continue
        else:
            raise ValueError("Invalid file type. The file must be a Shapefile (.shp), GeoJSON (.geojson), GeoTiff (.tif), Point Cloud (.las), png (.png), or jpeg (.jpeg).")

        minx.append(bounds[0])
        miny.append(bounds[1])
        maxx.append(bounds[2])
        maxy.append(bounds[3])

    if no_geolocation_data and not (minx and miny and maxx and maxy):  # No bounds were added
        return None

    union_bounds = (min(minx), min(miny), max(maxx), max(maxy))
    return union_bounds





# FUNCTION 15: CALCULATE INITIAL GEOHASH
def calculate_initial_geohash(bounds, precision):
    """
        Calculates an initial geohash that represents the center of a bounding box.

        Args:
            bounds (tuple): A tuple of four values representing the geographical bounds.
            precision (int): The initial geohash precision level.

        Returns:
            str: A geohash that represents the center of the bounding box.
    """
    center_lng = (bounds[0] + bounds[2]) / 2  # calculate center longitude
    center_lat = (bounds[1] + bounds[3]) / 2  # calculate center latitude
    geohash = gh.encode(center_lat, center_lng, precision = precision)  # calculate geohash of center point with initial precision
    return geohash





# FUNCTION 16: TEST COVERAGE
def check_coverage(geohash, bounds):
    """
        Checks if a geohash completely covers a bounding box.

        Args:
            geohash (str): A geohash.
            bounds (tuple): A tuple of four values representing the geographical bounds.

        Returns:
            bool: True if the geohash completely covers the bounding box, False otherwise.
    """
    lat_centroid, lon_centroid, lat_err, lon_err = gh.decode_exactly(geohash)  # decode geohash to its bounding box
    gh_bounds = {
        's': lat_centroid - lat_err,
        'w': lon_centroid - lon_err,
        'n': lat_centroid + lat_err,
        'e': lon_centroid + lon_err
    }
    covers_area = gh_bounds['s'] <= bounds[1] and gh_bounds['w'] <= bounds[0] and gh_bounds['n'] >= bounds[3] and gh_bounds['e'] >= bounds[2]
    # print(f"Does geohash {geohash} cover the entire area? {'Yes' if covers_area else 'No'}")
    return covers_area





# FUNCTION 17: Function to identify a list of smallest possible geohash which covers a given study area
# This function is useful when we are not able to bound a study area in 1 geohash
def generate_geohashes(bounds):
    """
        Generates a list of geohashes that together cover a bounding box.

        Args:
            bounds (tuple): A tuple of four values representing the geographical bounds.

        Returns:
            list of str: A list of geohashes that together cover the bounding box.
    """
    lat_step = (bounds[3] - bounds[1]) / 5.0
    lon_step = (bounds[2] - bounds[0]) / 5.0
    geohashes = set()  # change this to a set to ensure uniqueness

    for lat in range(0, 5):
        for lon in range(0, 5):
            min_lat = bounds[1] + lat * lat_step
            max_lat = min_lat + lat_step
            min_lon = bounds[0] + lon * lon_step
            max_lon = min_lon + lon_step
            center_lat = (min_lat + max_lat) / 2.0
            center_lon = (min_lon + max_lon) / 2.0
            geohash = gh.encode(center_lat, center_lon, precision = 1)
            geohashes.add(geohash)  # add the geohash to the set

    return list(geohashes)  # convert back to a list for the return





# FUNCTION 18: IDENTIFY THE EXTREMES, PRECISION ADJUSTMENTS AND ITERATIVE REFINEMENT
# FUNCTION TO IDENTIFY THE SMALLEST POSSIBLE GEOHASH WHICH COVERS A GIVEN STUDY AREA
def find_smallest_geohash(dataset, initial_precision = 10):
    """
        Finds the smallest geohash that covers the geographical area represented by the given dataset.

        Args:
            dataset (list of str): A list of file names representing the dataset.
            initial_precision (int, optional): The initial geohash precision level. Defaults to 10.

        Returns:
            str or list of str: The smallest geohash that covers the geographical area of the dataset,
                                or a list of such geohashes if a single geohash cannot cover the entire area.
                                Returns '7zzzzzzzzz' if no geolocation data is found specifically in the JPEG adn PNG dataset.
    """
    # A list of dataset instead of just one
    if isinstance(dataset, str):
        dataset = [dataset]  # If a single file is provided, turn it into a list

    bounds = load_and_calculate_union_bounds(dataset)

    if bounds is None:  # No geolocation data found in any JPG/PNG file
        return '7zzzzzzzzz'

    geohash = calculate_initial_geohash(bounds, initial_precision)  # Calculate initial geohash
    covers_area = check_coverage(geohash, bounds)  # Test coverage

    # If the geohash bounding box doesn't cover the entire city, decrement precision
    while not covers_area and initial_precision > 1:  # Precision adjustment
        initial_precision -= 1  # Iterative refinement
        geohash = calculate_initial_geohash(bounds, initial_precision)
        covers_area = check_coverage(geohash, bounds)

    # Ensure the final geohash covers the entire area
    if covers_area:
        smallest_geohash = geohash
    else:
        geohashes = generate_geohashes(bounds)  # Here we generate all geohashes for the area
        # If there's only one geohash, return it as a string, and not a list
        smallest_geohash = geohashes[0] if len(geohashes) == 1 else geohashes

    return smallest_geohash





# END OF THE PYTHON SCRIPT