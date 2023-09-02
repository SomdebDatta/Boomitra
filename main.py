from utility.constants import Constants
from utility.logger import get_logger
from utility.sentinel_imagery import read_geotiff

LOGGER = get_logger("Main Module.")


def main():
    """
    This is the main function.
    """
    LOGGER.debug("NDVI Pipeline started...")
    read_geotiff(vector_path=Constants.POLYGON_PATH.value)
    LOGGER.debug("NDVI Pipeline finished.")


if __name__ == "__main__":
    main()
