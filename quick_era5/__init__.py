from . import era5_converter
from . import era5_downloader

# check netCDF4's availability
try:
    import netCDF4
except ImportError:
    raise ImportError("netCDF4 is not installed, please install it by running 'pip install netCDF4'.")
