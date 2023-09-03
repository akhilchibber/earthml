import os
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from scipy.ndimage import filters
from osgeo import gdal

# Apply Orbit File
def apply_orbit_file(input_file, orbit_file, output_file):
    # open the input dataset
    src = gdal.Open(input_file, gdal.GA_ReadOnly)

    # read the metadata
    metadata = src.GetMetadata()

    # update the metadata with the orbit file
    metadata['Orbit File'] = orbit_file

    # create the output dataset
    driver = gdal.GetDriverByName('GTiff')
    dst = driver.CreateCopy(output_file, src)

    # set the updated metadata
    dst.SetMetadata(metadata)

    # close the datasets
    src = None
    dst = None

    print('Orbit file applied')

# Thermal Noise Removal
def remove_thermal_noise(input_file, output_file):
    # read the input data
    with rasterio.open(input_file) as src:
        image = src.read(1)

    # compute the thermal noise
    thermal_noise = np.mean(image)

    # subtract the thermal noise from the image
    image_denoised = image - thermal_noise

    # write the denoised image to the output file
    with rasterio.open(output_file, 'w', **src.profile) as dst:
        dst.write(image_denoised, 1)

    print('Thermal noise removed')

# Radiometric Correction
def radiometric_correction(input_file, output_file):
    # read the input data
    with rasterio.open(input_file) as src:
        image = src.read(1)

    # apply radiometric correction
    # NOTE: this is a simplified example and may not be accurate
    calibration_constant = 1  # Replace with actual calibration constant
    image_calibrated = image * calibration_constant

    # write the calibrated image to the output file
    with rasterio.open(output_file, 'w', **src.profile) as dst:
        dst.write(image_calibrated, 1)

    print('Radiometric correction completed')

# Speckle Filtering
def speckle_filtering(input_file, output_file):
    # read the input data
    with rasterio.open(input_file) as src:
        image = src.read(1)

    # apply speckle filtering
    # NOTE: this is a simplified example and may not be accurate
    image_filtered = filters.median_filter(image, size=3)

    # write the filtered image to the output file
    with rasterio.open(output_file, 'w', **src.profile) as dst:
        dst.write(image_filtered, 1)

    print('Speckle filtering completed')

# Geometric Correction
def geometric_correction(input_file, output_file, dst_crs):
    # read the input data
    with rasterio.open(input_file) as src:
        transform, width, height = calculate_default_transform(src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({'crs': dst_crs, 'transform': transform, 'width': width, 'height': height})

        with rasterio.open(output_file, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(source=rasterio.band(src, i),
                          destination=rasterio.band(dst, i),
                          src_transform=src.transform,
                          src_crs=src.crs,
                          dst_transform=transform,
                          dst_crs=dst_crs,
                          resampling=Resampling.bilinear)

    print('Geometric correction completed')

# Final Function to perform entire pre-processing
def preprocess_s1(input_file, orbit_file, output_file, dst_crs):
    # create temporary files
    temp_file1 = 'temp1.tif'
    temp_file2 = 'temp2.tif'

    # apply orbit file
    apply_orbit_file(input_file, orbit_file, temp_file1)

    # remove thermal noise
    remove_thermal_noise(temp_file1, temp_file2)

    # apply radiometric correction
    radiometric_correction(temp_file2, temp_file1)

    # apply speckle filtering
    speckle_filtering(temp_file1, temp_file2)

    # apply geometric correction
    geometric_correction(temp_file2, output_file, dst_crs)

    # remove temporary files
    os.remove(temp_file1)
    os.remove(temp_file2)
