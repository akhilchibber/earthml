import os
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from scipy.ndimage import filters

# Radiometric Calibration
def radiometric_calibration(input_file, output_file):
    # read the input data
    with rasterio.open(input_file) as src:
        image = src.read(1)

    # apply radiometric calibration
    # NOTE: this is a simplified example and may not be accurate
    calibration_constant = 1  # Replace with actual calibration constant
    image_calibrated = image * calibration_constant

    # write the calibrated image to the output file
    with rasterio.open(output_file, 'w', **src.profile) as dst:
        dst.write(image_calibrated, 1)

    print('Radiometric calibration completed')

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
                reproject(source=rasterio.band(src, i), destination=rasterio.band(dst, i), src_transform=src.transform, src_crs=src.crs, dst_transform=transform, dst_crs=dst_crs, resampling=Resampling.bilinear)

    print('Geometric correction completed')

# Final Function to perform entire pre-processing
def preprocess_terra_sar_x(input_file, output_file, dst_crs):
    # create temporary files
    temp_file1 = 'temp1.tif'
    temp_file2 = 'temp2.tif'

    # apply radiometric calibration
    radiometric_calibration(input_file, temp_file1)

    # apply speckle filtering
    speckle_filtering(temp_file1, temp_file2)

    # apply geometric correction
    geometric_correction(temp_file2, output_file, dst_crs)

    # remove temporary files
    os.remove(temp_file1)
    os.remove(temp_file2)
