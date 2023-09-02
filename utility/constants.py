import os
from enum import Enum
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]


class Constants(Enum):
    LOG_FILE_NAME = os.path.join("Boomitra", "app.log")
    BUCKET_NAME = "sentinel-2-l2a-cogs"
    POLYGON_PATH = os.path.join(ROOT, "Boomitra", "config", "sample_polygon.geojson")
    GEOTIFF_NIR_URL = "s3://sentinel-cogs/sentinel-s2-l2a-cogs/36/N/YF/2023/6/S2B_36NYF_20230605_0_L2A/B08.tif"
    GEOTIFF_RED_URL = "s3://sentinel-cogs/sentinel-s2-l2a-cogs/36/N/YF/2023/6/S2B_36NYF_20230605_0_L2A/B04.tif"
    OUTPUT_FOLDER_PATH = os.path.join(ROOT, "Boomitra", "output_files")
    POLYGON_ID_FIELD = "Partner ID"
