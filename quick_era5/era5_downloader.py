import datetime
import gcsfs
import os
import pickle
import xarray
gcs = gcsfs.GCSFileSystem(token='anon')

# config
local_full_era5_zarr_at = os.path.abspath(__file__).replace('era5_downloader.py', 'asset/full_era5.pkl')
cache_era5_folder = os.path.abspath(__file__).replace('era5_downloader.py', 'cache/era5/')
era5_gcp_path = 'gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3'
expire_days = 14


def download_era5_data_from_gcs(variable_list: list, from_datetime: datetime.datetime, to_datetime: datetime.datetime, time_interval: int = 1) -> xarray.Dataset:
    """
    Download the era5 data from GCS and return the xarray dataset.

    Args:
        variable_list: list, list of variables to download.
        from_date: datetime.datetime, start datetime of the data.
        to_date: datetime.datetime, end datetime (include this datetime) of the data.
        data_steps: int, hours between each data.

    Returns:
        xarray.Dataset, the era5 dataset.
    """
    # [load the full era5 zarr file]
    try:
        full_era5 = pickle.load(open(local_full_era5_zarr_at, 'rb'))
    except FileNotFoundError:
        download_full_era5_zarr()  # download the full era5 zarr file if not exists
        full_era5 = pickle.load(open(local_full_era5_zarr_at, 'rb'))
    valid_time_start = datetime.datetime.strptime(full_era5.valid_time_start, '%Y-%m-%d')
    valid_time_stop = datetime.datetime.strptime(full_era5.valid_time_stop, '%Y-%m-%d')
    # valid_level = list(full_era5.level.to_series())

    # [check input]
    # variable_list should be a list
    if not isinstance(variable_list, list):
        raise ValueError(f"variable_list should be a list, but got {type(variable_list)}")

    # all variables should be in the era5 dataset variable list
    for variable in variable_list:
        if variable not in full_era5.data_vars:
            raise ValueError(f"variable {variable} is not in the era5 dataset, if you want to check the variables, please run `metorology.era5_downloader.show_era5_variables()`")

    # from_datetime should be a datetime.datetime object
    if not isinstance(from_datetime, datetime.datetime):
        raise ValueError(f"from_datetime should be a datetime.datetime object, but got {type(from_datetime)}")

    # from_datetime should have timezone information
    if from_datetime.tzinfo is None:
        raise ValueError(f"from_datetime should have timezone information, but from_datetime.tzinfo is None. For more information, please refer to https://docs.python.org/3/library/datetime.html#datetime.datetime.tzinfo")
    else:
        # convert the timezone to UTC
        from_datetime = from_datetime.astimezone(datetime.timezone.utc)
        from_datetime = from_datetime.replace(tzinfo=None)

    # from_datetime should be at the beginning of the hour (min and sec and microsec should be 0)
    if from_datetime.minute != 0 or from_datetime.second != 0 or from_datetime.microsecond != 0:
        raise ValueError(f"from_datetime should be at the beginning of the hour, but got {from_datetime}")

    # to_datetime should be a datetime.datetime object
    if not isinstance(to_datetime, datetime.datetime):
        raise ValueError(f"to_datetime should be a datetime.datetime object, but got {type(to_datetime)}")

    # to_datetime should have timezone information
    if to_datetime.tzinfo is None:
        raise ValueError(f"to_datetime should have timezone information, but to_datetime.tzinfo is None. For more information, please refer to https://docs.python.org/3/library/datetime.html#datetime.datetime.tzinfo")
    else:
        # convert the timezone to UTC
        to_datetime = to_datetime.astimezone(datetime.timezone.utc)
        to_datetime = to_datetime.replace(tzinfo=None)

    # to_datetime should be at the beginning of the hour (min and sec and microsec should be 0)
    if to_datetime.minute != 0 or to_datetime.second != 0 or to_datetime.microsecond != 0:
        raise ValueError(f"to_datetime should be at the beginning of the hour, but got {to_datetime}")

    # time_interval should be an integer
    if from_datetime >= to_datetime:
        raise ValueError(f"from_datetime should be earlier than to_datetime, but got from_datetime: {from_datetime}, to_datetime: {to_datetime}")

    # from_datetime should be in the valid range of the era5 dataset
    if from_datetime < valid_time_start:
        raise ValueError(f"from_datetime should be in GCS ERA5 data set valid range({valid_time_start}, {valid_time_stop}), but got from_datetime: {from_datetime}")

    # to_datetime should be in the valid range of the era5 dataset
    if to_datetime > valid_time_stop:
        raise ValueError(f"to_datetime should be in GCS ERA5 data set valid range({valid_time_start}, {valid_time_stop}), but got to_datetime: {to_datetime}")

    # time_interval should be greater than 0
    if time_interval <= 0:
        raise ValueError(f"data_steps should be greater than 0, but got {time_interval}")

    # [set the cache file information]
    variable_list = sorted(variable_list)  # ['geopotential', 'temperature', ...]
    variable_list_str = '_'.join(variable_list)  # 'geopotential_temperature_...'
    cache_expire_date = datetime.datetime.now() + datetime.timedelta(days=expire_days)
    cache_expire_date_str = cache_expire_date.strftime('%Y%m%d%H%M%S')  # '20230101120000'
    from_datetime_str = from_datetime.strftime('%Y%m%d%H')  # '2023010112'
    to_datetime_str = to_datetime.strftime('%Y%m%d%H')  # '2023010212'
    cache_name = f'{from_datetime_str}_{to_datetime_str}_{time_interval}_{variable_list_str}'  # '20230101_20230102_1_geopotential_temperature_...'

    # [check if the cache exists]
    cache_file_list = [file for file in os.listdir(cache_era5_folder) if file.startswith(cache_name)]
    cache_file_exist = len(cache_file_list) > 0
    if cache_file_exist:
        original_cache_file_name = cache_file_list[0]
        original_cache_file_path = os.path.join(cache_era5_folder, original_cache_file_name)
        new_cache_file_name = f"{cache_name}_{cache_expire_date_str}.nc"
        new_cache_file_path = os.path.join(cache_era5_folder, new_cache_file_name)
        xarr = xarray.open_dataset(original_cache_file_path, engine='netcdf4')
        os.rename(original_cache_file_path, new_cache_file_path)

    # [remove expired cache]
    # while you run the code, if the cache is older than 14 days, remove the cache
    remove_cache()

    # [return the cache if exists]
    if cache_file_exist:
        return xarr

    # [download the data]
    start = from_datetime
    end = to_datetime
    step = time_interval
    sliced_era5 = (
        full_era5
        [variable_list]
        .sel(time=slice(start, end, step))
        .compute()
    )

    # [save the data to the cache]
    cache_file_path = os.path.join(cache_era5_folder, f"{cache_name}_{cache_expire_date_str}.nc")
    sliced_era5.to_netcdf(cache_file_path)

    return sliced_era5


def show_era5_variables() -> list:
    """
    Show the variables in the era5 dataset.

    Args:
        None
    Returns:
        list, list of variables in the era5 dataset.
    """
    # load the full era5 zarr file
    try:
        full_era5 = pickle.load(open(local_full_era5_zarr_at, 'rb'))
    except FileNotFoundError:
        download_full_era5_zarr()  # download the full era5 zarr file if not exists
        full_era5 = pickle.load(open(local_full_era5_zarr_at, 'rb'))

    # show the variables
    var_list = list(full_era5.data_vars)
    return var_list


def download_full_era5_zarr() -> None:
    """
    Download the full era5 zarr file from GCS and save it to the local directory.

    Args:
        None
    Returns:
        None
    """
    # check if the file exists
    if os.path.exists(local_full_era5_zarr_at):
        return

    # download full era5 zarr file if not exists
    era5_path = era5_gcp_path
    full_era5 = xarray.open_zarr(gcs.get_mapper(era5_path), chunks=None)
    with open(local_full_era5_zarr_at, 'wb') as f:
        pickle.dump(full_era5, f)
    return


def remove_cache() -> None:
    for cache_file in os.listdir(cache_era5_folder):
        expire_date_str = cache_file.split('_')[-1].split('.')[0]
        expire_date = datetime.datetime.strptime(expire_date_str, '%Y%m%d%H%M%S')
        if expire_date < datetime.datetime.now():
            os.remove(os.path.join(cache_era5_folder, cache_file))