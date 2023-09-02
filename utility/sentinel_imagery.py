import csv
import os
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.features import geometry_mask, geometry_window
from rasterio.plot import show
from rasterio.windows import transform
from shapely.geometry import shape
from utility.constants import Constants
from utility.logger import get_logger

LOGGER = get_logger("Get GeoTiff")


def read_geotiff(vector_path: str):
    """
    This is the orchestrator function.
    Steps followed.
    1. Opening the geojson and converting it to EPSG:32636 CRS to be in line with the input bands.
    2. Opening the Near Infra Red (NIR) and Red bands.
    3. Reading only a subset of the bands that is overlaying the input geojson given.
    4. Calculating the Normalized difference vegetation index (NDVI).
    5. Calculating the relevant stats and saving in a csv file.
    6. Saving the ndvi.tif file.
    7. Saving the ndvi.png file.

    Args:
        vector_path: str: A string having a path to the input vector.

    """
    polygon_gdf = gpd.read_file(vector_path)
    polygon_gdf = polygon_gdf.to_crs("EPSG:32636")

    with rasterio.Env(AWS_NO_SIGN_REQUEST="YES"):
        with rasterio.open(
            Constants.GEOTIFF_NIR_URL.value
        ) as nir_fullscale, rasterio.open(
            Constants.GEOTIFF_RED_URL.value
        ) as red_fullscale:
            LOGGER.info("NIR and Red band objects read successfully.")
            LOGGER.info(f"CRS of nir band - {nir_fullscale.crs}")

            for feature in polygon_gdf.iterfeatures(show_bbox=True):
                LOGGER.info("Creating a window of the Region of Interest...")
                window = geometry_window(nir_fullscale, [feature["geometry"]])
                window_transform = transform(window, nir_fullscale.transform)
                window_shape = (window.height, window.width)
                LOGGER.info("Window created.")

                LOGGER.info("Reading the NIR and Red band windows.")
                nir = nir_fullscale.read(window=window, masked=True).astype("float32")
                red = red_fullscale.read(window=window, masked=True).astype("float32")

                mask = geometry_mask(
                    [feature["geometry"]], window_shape, window_transform
                )
                nir.mask += mask
                red.mask += mask

                LOGGER.info("Starting NDVI Calculation...")
                ndvi = calculate_ndvi(nir=nir, red=red)
                LOGGER.info(f"NDVI calculated.")

                LOGGER.info("Calculating statistics for the NDVI...")
                calculate_stats(ndvi=ndvi)

                LOGGER.info("Updating metadata...")
                meta = nir_fullscale.meta
                meta.update(
                    {
                        "driver": "GTiff",
                        "dtype": ndvi.dtype,
                        "height": window.height,
                        "width": window.width,
                        "transform": window_transform,
                    }
                )

                fig, ax = plt.subplots(1, 1)
                show(ndvi, ax=ax)
                # polygon_gdf.plot(ax=ax, edgecolor="red")
                plt.show()

                ndvi_path = os.path.join(
                    Constants.OUTPUT_FOLDER_PATH.value,
                    f"ndvi.tif",
                )

                with rasterio.open(ndvi_path, "w", **meta) as dst:
                    dst.write(ndvi)

                Path(Constants.OUTPUT_FOLDER_PATH.value).mkdir(
                    parents=True, exist_ok=True
                )

                LOGGER.info(
                    f"NDVI tif saved at location - {Constants.OUTPUT_FOLDER_PATH.value}"
                )

                # Saving the PNG file
                plt.imsave(
                    os.path.join(Constants.OUTPUT_FOLDER_PATH.value, "ndvi.jpg"),
                    ndvi[0],
                    cmap=plt.cm.summer,
                )
                LOGGER.info(
                    f"NDVI png saved at location - {Constants.OUTPUT_FOLDER_PATH.value}"
                )


def calculate_ndvi(nir, red):
    """
    This function calculates the NDVI.

    Args:
        nir: A numpy array having the NIR band values.
        red: A numpy array having the Red band values.

    Returns:
        A numpy array having the NDVI band values.
    """
    return (nir - red) / (nir + red)


def calculate_stats(ndvi):
    """
    This function is used to calculate the relevant statistics - Mean, Max, Min and, then save it.

    Args:
        ndvi: A numpy array having the NDVI values."""
    field_names = ["Mean", "Max", "Min"]
    mean = np.mean(ndvi)
    LOGGER.info("Mean calculated.")

    maxi = np.max(ndvi)
    LOGGER.info("Max calculated.")

    mini = np.min(ndvi)
    LOGGER.info("Min calculated")

    stats_list = [{"Mean": mean, "Max": maxi, "Min": mini}]

    with open(
        os.path.join(Constants.OUTPUT_FOLDER_PATH.value, "Stats.csv"), "w"
    ) as csv_file:
        write = csv.DictWriter(csv_file, fieldnames=field_names)
        write.writeheader()
        write.writerows(stats_list)
    LOGGER.info(f"Statistics saved at location - {Constants.OUTPUT_FOLDER_PATH.value}")
