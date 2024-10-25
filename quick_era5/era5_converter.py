from affine import Affine
import datetime
import numpy as np
import pandas as pd
import rasterio
import xarray


def era5_xarray_to_netcdf(xarr: xarray.core.dataset.Dataset, save_at: str) -> None:
    """
    Save the xarray dataset to a netcdf file.

    Args:
        xarr, xarray.core.dataset.Dataset, the xarray dataset to save.
        file_path, str, the file path to save the xarray dataset.
    Returns:
        None
    """
    # check
    if not isinstance(xarr, xarray.core.dataset.Dataset):
        raise ValueError("The input xarr should be an xarray dataset.")
    if not isinstance(save_at, str):
        raise ValueError("The input save_at should be a string.")
    if not save_at.lower().endswith(".nc"):
        raise ValueError("The input save_at should be a '.nc' file.")

    xarr.to_netcdf(save_at)
    return None


def era5_xarray_to_geotiff(xarr: xarray.core.dataset.Dataset, variable: str, z: int | float, time: datetime.datetime, save_at: str) -> None:
    """
    Save the specified variable, pressure level, time data in the xarray dataset to a geotiff file.

    Args:
        xarr: xarray.core.dataset.Dataset, the xarray dataset to save.
        variable: str, the variable to save.
        z: int or float or None, the z level to save, if data has only one level, use None.
        time: datetime.datetime, the time to save, if timezone is None, it will be converted to UTC.
        save_at: str, the file path to save geotiff file.

    Returns:
        None
    """
    # [check input]
    # xarr should be an xarray dataset
    if not isinstance(xarr, xarray.core.dataset.Dataset):
        raise ValueError("The input xarr should be an xarray dataset.")
    
    # variable should be a string
    if not isinstance(variable, str):
        raise ValueError("The input variable should be a string.")
    
    # z should be a float or an integer
    if (not isinstance(z, (float, int))) and (z is not None):
        raise ValueError("The input z should be a float or an integer or None.")
    
    # time should be a datetime object
    if not isinstance(time, datetime.datetime):
        raise ValueError("The input time should be a datetime.datetime object.")
    
    # time should be in UTC, if not, convert it to UTC
    if time.tzinfo is None:
        time = time.replace(tzinfo=datetime.timezone.utc)
    else:
        time = time.astimezone(datetime.timezone.utc)

    # variable should be in the xarr
    available_variables = list(xarr.data_vars)
    if variable not in available_variables:
        raise ValueError(f"The input variable({variable}) should be in the xarray dataset, available variables: {available_variables}")
    
    # z should be in the xarr
    try:
        available_levels = list(xarr[variable].level.values)
    except AttributeError:
        z = "only one"
        available_levels = []
    if z not in available_levels and z != "only one":
        raise ValueError(f"The input z({z}) should be in the xarray dataset, available levels: {available_levels}")
    
    # time should be in the xarr
    available_times = list(map(lambda x: (pd.to_datetime(x).to_pydatetime().replace(tzinfo=datetime.timezone.utc)), list(xarr.time.values)))
    if time not in available_times:
        raise ValueError(f"The input time {time} should be in the xarray dataset, available times: {available_times}")
    
    # save_at should be a string
    if not isinstance(save_at, str):
        raise ValueError("The input save_at should be a string.")
    
    # save_at should be a '.tif' file
    if not save_at.lower().endswith(".tif") and not save_at.lower().endswith(".tiff"):
        raise ValueError("The input save_at should be a '.tif' or '.tiff' file.")

    # [get data array]
    variable = variable
    time = np.datetime64(time.replace(tzinfo=None))
    if z == "only one":
        array = xarr[variable].sel(time=time).values
    else:
        level = int(z)
        array = xarr[variable].sel(level=level, time=time).values

    # get lat lon info
    lat_list = list(xarr.latitude.values)
    lon_list = list(xarr.longitude.values)
    delta_lat = abs(lat_list[1] - lat_list[0])
    delta_lon = abs(lon_list[1] - lon_list[0])

    # longitude is from 0 to 360 originally, we need to convert it to -180 to 180
    lon_gt_180 = [i for i, lon in enumerate(lon_list) if lon >= 180][0]
    lon_list = lon_list[lon_gt_180:] + lon_list[:lon_gt_180]
    lon_list = [lon - 360 if lon >= 180 else lon for lon in lon_list]
    array = np.concatenate((array[:, lon_gt_180:], array[:, :lon_gt_180]), axis=1)

    # calculate georeference info
    north = lat_list[0] + delta_lat / 2
    west = lon_list[0] - delta_lon / 2
    delta_x = delta_lon
    delta_y = delta_lat
    height = array.shape[0]
    width = array.shape[1]
    transform = Affine(delta_x, 0, west, 0, -delta_y, north)
    crs = rasterio.crs.CRS.from_epsg(4326)

    # save
    with rasterio.open(
        save_at,
        mode="w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=np.float32,
        nodata=np.nan,
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(array, 1)

    return None


def era5_xarray_to_nparray(xarr: xarray.core.dataset.Dataset, variable: str, z: int | float, time: datetime.datetime) -> np.ndarray:
    """
    Save the specified variable, pressure level, time data in the xarray dataset to a numpy array.

    Args:
        xarr: xarray.core.dataset.Dataset, the xarray dataset to save.
        variable: str, the variable to save.
        z: int or float or None, the z level to save, if data has only one level, use None.
        time: datetime.datetime, the time to save, if timezone is None, it will be converted to UTC.

    Returns:
        np.ndarray, the numpy array of the specified variable, pressure level, time data.
    """
    # [check input]
    # xarr should be an xarray dataset
    if not isinstance(xarr, xarray.core.dataset.Dataset):
        raise ValueError("The input xarr should be an xarray dataset.")

    # variable should be a string
    if not isinstance(variable, str):
        raise ValueError("The input variable should be a string.")

    # z should be a float or an integer
    if (not isinstance(z, (float, int))) and (z is not None):
        raise ValueError("The input z should be a float or an integer or None.")

    # time should be a datetime object
    if not isinstance(time, datetime.datetime):
        raise ValueError("The input time should be a datetime.datetime object.")

    # time should be in UTC, if not, convert it to UTC
    if time.tzinfo is None:
        time = time.replace(tzinfo=datetime.timezone.utc)
    else:
        time = time.astimezone(datetime.timezone.utc)

    # variable should be in the xarr
    available_variables = list(xarr.data_vars)
    if variable not in available_variables:
        raise ValueError(f"The input variable({variable}) should be in the xarray dataset, available variables: {available_variables}")

    # z should be in the xarr
    try:
        available_levels = list(xarr[variable].level.values)
    except AttributeError:
        z = "only one"
        available_levels = []
    if z not in available_levels and z != "only one":
        raise ValueError(f"The input z({z}) should be in the xarray dataset, available levels: {available_levels}")
    
    # time should be in the xarr
    available_times = list(map(lambda x: (pd.to_datetime(x).to_pydatetime().replace(tzinfo=datetime.timezone.utc)), list(xarr.time.values)))
    if time not in available_times:
        raise ValueError(f"The input time {time} should be in the xarray dataset, available times: {available_times}")

    # [get data array]
    variable = variable
    time = np.datetime64(time.replace(tzinfo=None))
    if z == "only one":
        array = xarr[variable].sel(time=time).values
    else:
        level = int(z)
        array = xarr[variable].sel(level=level, time=time).values

    # [get lat lon info]
    lat_list = list(xarr.latitude.values)
    lon_list = list(xarr.longitude.values)
    delta_lat = abs(lat_list[1] - lat_list[0])
    delta_lon = abs(lon_list[1] - lon_list[0])

    # [reorder the array]
    # longitude is from 0 to 360 originally, we need to convert it to -180 to 180
    lon_gt_180 = [i for i, lon in enumerate(lon_list) if lon >= 180][0]
    lon_list = lon_list[lon_gt_180:] + lon_list[:lon_gt_180]
    lon_list = [lon - 360 if lon >= 180 else lon for lon in lon_list]
    array = np.concatenate((array[:, lon_gt_180:], array[:, :lon_gt_180]), axis=1)

    return array
