import datetime
import gcsfs
import os
import pickle
import xarray
gcs = gcsfs.GCSFileSystem(token='anon')

# config
base_path = os.path.dirname(os.path.abspath(__file__))
local_full_era5_zarr_at = os.path.join(base_path, 'asset', 'full_era5.pkl')
cache_era5_folder = os.path.join(base_path, 'cache', 'era5')

era5_gcp_path = 'gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3'
expire_days = 14

# constants
utc = datetime.timezone.utc


def download_era5_data_from_gcs(
    variable_list: list,
    from_datetime: datetime.datetime,
    to_datetime: datetime.datetime,
    time_interval: int = 1,
    level_range: tuple | int = (1000, 0),
    latitude_range: tuple = (-90, 90),
    longitude_range: tuple = (0, 360),
    longitude_shift: bool = True,
) -> xarray.Dataset:
    """
    Download the era5 data from GCS and return the xarray dataset.

    Args:
        variable_list (list): 
            List of variables to download. e.g. ['geopotential', 'temperature']
        from_datetime (datetime.datetime): 
            Start datetime of the data, must include timezone information. e.g. datetime.datetime(2023, 1, 1, 12, tzinfo=datetime.timezone.utc)
        to_datetime (datetime.datetime): 
            End datetime (include this datetime) of the data, must include timezone information. e.g. datetime.datetime(2023, 1, 2, 12, tzinfo=datetime.timezone.utc)
        time_interval (int): 
            Hours between each data. Default is True.
        level_range (tuple or int): 
            Level range to download. If int, download only the level. If tuple, download the range of levels (include). Default is (1000, 0).
        latitude_range (tuple): 
            Latitude range to download. Default is (-90, 90).
        longitude_range (tuple): 
            Longitude range to download. Default is (0, 360).
        longitude_shift (bool):
            If True, shift the longitude from -180~180 to 0-360. Default is True.

    Returns:
        xarray.Dataset: The era5 dataset.
    """
    # [update the local era5 if have new data]
    update_if_have_new_era5()

    # [load the full era5 zarr file]
    full_era5 = _load_full_era5()
    valid_time_start = datetime.datetime.strptime(full_era5.valid_time_start, '%Y-%m-%d')
    valid_time_stop = datetime.datetime.strptime(full_era5.valid_time_stop, '%Y-%m-%d')
    valid_level_start = sorted(list(full_era5.level.to_series()))[0]
    valid_level_stop = sorted(list(full_era5.level.to_series()))[-1]

    # [check input]
    _variable_list_should_be_list(variable_list)
    _all_var_should_be_in_era5_dataset_var_list(full_era5, variable_list)
    _from_datetime_should_be_datetime(from_datetime)
    _from_datetime_should_have_timezone(from_datetime)
    from_datetime = (from_datetime.astimezone(utc)).replace(tzinfo=None)
    _from_datetime_should_be_at_the_beginning_of_the_hour(from_datetime)
    _to_datetime_should_be_datetime(to_datetime)
    _to_datetime_should_have_timezone(to_datetime)
    to_datetime = (to_datetime.astimezone(utc)).replace(tzinfo=None)
    _to_datetime_should_be_at_the_beginning_of_the_hour(to_datetime)
    _from_datetime_should_be_earlier_than_to_datetime(from_datetime, to_datetime)
    _from_datetime_should_be_in_valid_range(from_datetime, valid_time_start, valid_time_stop)
    _to_datetime_should_be_in_valid_range(to_datetime, valid_time_start, valid_time_stop)
    _level_range_should_be_tuple_or_int(level_range)
    _level_range_should_in_valid_range(level_range, valid_level_start, valid_level_stop)
    level_range = _level_range_adjustment(level_range)  # 由小到大，int改為相同的tuple
    _latitude_range_should_be_tuple(latitude_range)
    _latitude_range_should_in_valid_range(latitude_range)
    latitude_range = _latitude_range_adjustment(latitude_range)  # 由小到大
    _longitude_range_should_be_tuple(longitude_range)
    _longitude_range_should_in_valid_range(longitude_range, longitude_shift)
    longitude_range = _longitude_range_adjustment(longitude_range)  # 由小到大
    _time_interval_should_be_positive(time_interval)

    # [set the cache file information]
    _, cache_expire_date_str = _calculate_cache_expire_date()
    cache_name = _generate_cache_name(from_datetime, to_datetime, time_interval, variable_list, level_range, latitude_range, longitude_range, longitude_shift)

    # [check if the cache exists]
    if _cache_file_exist(cache_name):
        xarr = _get_cache_file_xarr(cache_name)
        _rename_cache_file(cache_name, cache_expire_date_str)

    # [remove expired cache]
    # while you run the code, if the cache is older than 14 days, remove the cache
    remove_expired_cache()

    # [return the cache if exists]
    if _cache_file_exist(cache_name):
        return xarr

    # [shift the longitude if needed]
    if longitude_shift:
        full_era5 = full_era5  # 下載的預設狀況就是有shift過的
    else:
        # print(full_era5.longitude)
        full_era5 = full_era5.assign_coords(longitude=(((full_era5.longitude + 180) % 360) - 180)).sortby('longitude')

    # [download the data]
    try:
        sliced_era5 = (
            full_era5
            [variable_list]
            .sel(
                time=slice(from_datetime, to_datetime, time_interval),  # ???
                level=slice(level_range[0], level_range[1]),
                latitude=slice(latitude_range[0], latitude_range[1]),
                longitude=slice(longitude_range[0], longitude_range[1])
            )
        )
        sliced_era5 = sliced_era5.load()
    except Exception as e:
        if "'level' is not a valid dimension or coordinate" in str(e):
            sliced_era5 = (
                full_era5
                [variable_list]
                .sel(
                    time=slice(from_datetime, to_datetime, time_interval),
                    latitude=slice(latitude_range[0], latitude_range[1]),
                    longitude=slice(longitude_range[0], longitude_range[1])
                )
            )
            sliced_era5 = sliced_era5.load()
        else:
            raise ValueError(f"Error occurs when downloading the data, error message: {e}")

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


def remove_expired_cache() -> None:
    for cache_file in os.listdir(cache_era5_folder):
        expire_date_str = cache_file.split('_')[-1].split('.')[0]
        try:
            expire_date = datetime.datetime.strptime(expire_date_str, '%Y%m%d%H%M%S')
            if expire_date < datetime.datetime.now():
                os.remove(os.path.join(cache_era5_folder, cache_file))
        except:
            pass


# [sub functions]
def _load_full_era5() -> xarray.Dataset:
    """
    Try load the full era5 zarr file, if not exists, download it from GCS then load it.
    """
    try:
        full_era5 = pickle.load(open(local_full_era5_zarr_at, 'rb'))
    except FileNotFoundError:
        download_full_era5_zarr()  # download the full era5 zarr file if not exists
        full_era5 = pickle.load(open(local_full_era5_zarr_at, 'rb'))

    return full_era5


def get_latest_era5_end_time():
    era5_gcp_attr_path = 'gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3/.zattrs'
    era5_gcp_attr_content = eval(gcs.cat(era5_gcp_attr_path))
    latest_era5_end_time = datetime.datetime.strptime(era5_gcp_attr_content['valid_time_stop'], '%Y-%m-%d')
    return latest_era5_end_time


def get_local_era5_stop_time():
    full_era5 = _load_full_era5()
    valid_time_stop = datetime.datetime.strptime(full_era5.valid_time_stop, '%Y-%m-%d')
    return valid_time_stop


def update_if_have_new_era5():
    latest_era5_end_time = get_latest_era5_end_time()
    local_era5_stop_time = get_local_era5_stop_time()
    if latest_era5_end_time > local_era5_stop_time:
        os.remove(local_full_era5_zarr_at)
        download_full_era5_zarr()


def _generate_cache_name(from_datetime, to_datetime, time_interval, variable_list, level_range, latitude_range, longitude_range, longitude_shift):
    from_datetime_str = from_datetime.strftime('%Y%m%d%H')  # '2023010112'
    to_datetime_str = to_datetime.strftime('%Y%m%d%H')  # '2023010212'
    variable_list = sorted(variable_list)  # ['geopotential', 'temperature', ...]
    variable_list_str = '_'.join(variable_list)  # 'geopotential_temperature_...'
    cache_name = f'{from_datetime_str}_{to_datetime_str}_{time_interval}_{variable_list_str}_{level_range[0]}_{level_range[1]}_{latitude_range[0]}_{latitude_range[1]}_{longitude_range[0]}_{longitude_range[1]}_{longitude_shift}'
    return cache_name


def _calculate_cache_expire_date():
    """
    Calculate the cache expire date and return the datetime object and string.

    Returns:
        cache_expire_date (datetime.datetime): The cache expire date.
        cache_expire_date_str (str): The cache expire date in string format.
    """
    cache_expire_date = datetime.datetime.now() + datetime.timedelta(days=expire_days)
    cache_expire_date_str = cache_expire_date.strftime('%Y%m%d%H%M%S')  # '20230101120000'
    return cache_expire_date, cache_expire_date_str


def _cache_file_exist(cache_name):
    cache_file_list = [file for file in os.listdir(cache_era5_folder) if file.startswith(cache_name)]
    return len(cache_file_list) > 0


def _cache_file_path(cache_name):
    cache_file_list = [file for file in os.listdir(cache_era5_folder) if file.startswith(cache_name)]
    return os.path.join(cache_era5_folder, cache_file_list[0])


def _get_cache_file_xarr(cache_name):
    cache_file_path = _cache_file_path(cache_name)
    xarr = xarray.open_dataset(cache_file_path, engine='netcdf4')
    return xarr


def _rename_cache_file(cache_name, expire_date_str):
    cache_file_path = _cache_file_path(cache_name)
    new_cache_file_name = f"{cache_name}_{expire_date_str}.nc"
    new_cache_file_path = os.path.join(cache_era5_folder, new_cache_file_name)
    os.rename(cache_file_path, new_cache_file_path)


# [check functions]
def _variable_list_should_be_list(variable_list: list) -> None:
    if not isinstance(variable_list, list):
        raise ValueError(f"variable_list should be a list, but got {type(variable_list)}")


def _all_var_should_be_in_era5_dataset_var_list(full_era5: xarray.Dataset, variable_list: list) -> None:
    for variable in variable_list:
        if variable not in full_era5.data_vars:
            raise ValueError(f"variable {variable} is not in the era5 dataset, if you want to check the variables, please run `metorology.era5_downloader.show_era5_variables()`")


def _from_datetime_should_be_datetime(from_datetime: datetime.datetime) -> None:
    if not isinstance(from_datetime, datetime.datetime):
        raise ValueError(f"from_datetime should be a datetime.datetime object, but got {type(from_datetime)}")


def _from_datetime_should_have_timezone(from_datetime: datetime.datetime) -> None:
    if from_datetime.tzinfo is None:
        raise ValueError(f"from_datetime should have timezone information, but from_datetime.tzinfo is None. For more information, please refer to https://docs.python.org/3/library/datetime.html#datetime.datetime.tzinfo")


def _from_datetime_should_be_at_the_beginning_of_the_hour(from_datetime: datetime.datetime) -> None:
    if from_datetime.minute != 0 or from_datetime.second != 0 or from_datetime.microsecond != 0:
        raise ValueError(f"from_datetime should be at the beginning of the hour, but got {from_datetime}")


def _to_datetime_should_be_datetime(to_datetime: datetime.datetime) -> None:
    if not isinstance(to_datetime, datetime.datetime):
        raise ValueError(f"to_datetime should be a datetime.datetime object, but got {type(to_datetime)}")


def _to_datetime_should_have_timezone(to_datetime):
    if to_datetime.tzinfo is None:
        raise ValueError(f"to_datetime should have timezone information, but to_datetime.tzinfo is None. For more information, please refer to https://docs.python.org/3/library/datetime.html#datetime.datetime.tzinfo")


def _to_datetime_should_be_at_the_beginning_of_the_hour(to_datetime):
    if to_datetime.minute != 0 or to_datetime.second != 0 or to_datetime.microsecond != 0:
        raise ValueError(f"to_datetime should be at the beginning of the hour, but got {to_datetime}")


def _from_datetime_should_be_earlier_than_to_datetime(from_datetime, to_datetime):
    if from_datetime > to_datetime:
        raise ValueError(f"from_datetime should be earlier than to_datetime, but got from_datetime: {from_datetime}, to_datetime: {to_datetime}")


def _from_datetime_should_be_in_valid_range(from_datetime, valid_time_start, valid_time_stop):
    if from_datetime < valid_time_start:
        raise ValueError(f"from_datetime should be in GCS ERA5 data set valid range({valid_time_start}, {valid_time_stop}), but got from_datetime: {from_datetime}")


def _to_datetime_should_be_in_valid_range(to_datetime, valid_time_start, valid_time_stop):
    if to_datetime > valid_time_stop:
        raise ValueError(f"to_datetime should be in GCS ERA5 data set valid range({valid_time_start}, {valid_time_stop}), but got to_datetime: {to_datetime}")


def _level_range_should_be_tuple_or_int(level_range):
    if not isinstance(level_range, tuple) and not isinstance(level_range, int):
        raise ValueError(f"level_range should be tuple or int, but got {type(level_range)}")


def _level_range_should_in_valid_range(level_range, valid_level_start, valid_level_stop):
    if isinstance(level_range, tuple):
        if level_range[0] < valid_level_start or level_range[1] > valid_level_stop:
            raise ValueError(f"level_range should be in GCS ERA5 data set valid range({valid_level_start}, {valid_level_stop}), but got level_range: {level_range}")
    elif isinstance(level_range, int):
        if level_range < valid_level_start or level_range > valid_level_stop:
            raise ValueError(f"level_range should be in GCS ERA5 data set valid range({valid_level_start}, {valid_level_stop}), but got level_range: {level_range}")


def _level_range_adjustment(level_range):
    if isinstance(level_range, int):
        return (level_range, level_range)
    else:
        return (min(level_range), max(level_range))


def _latitude_range_should_be_tuple(latitude_range):
    if not isinstance(latitude_range, tuple):
        raise ValueError(f"latitude_range should be a tuple, but got {type(latitude_range)}")


def _latitude_range_should_in_valid_range(latitude_range):
    if latitude_range[0] < -90 or latitude_range[1] < -90 or latitude_range[0] > 90 or latitude_range[1] > 90:
        raise ValueError(f"latitude_range should be in GCS ERA5 data set valid range(-90, 90), but got latitude_range: {latitude_range}")


def _latitude_range_adjustment(latitude_range):
    return (max(latitude_range), min(latitude_range))


def _longitude_range_should_be_tuple(longitude_range):
    if not isinstance(longitude_range, tuple):
        raise ValueError(f"longitude_range should be a tuple, but got {type(longitude_range)}")


def _longitude_range_should_in_valid_range(longitude_range, longitude_shift):
    if longitude_shift:
        if longitude_range[0] < 0 or longitude_range[1] < 0 or longitude_range[0] > 360 or longitude_range[1] > 360:
            raise ValueError(f"longitude_range should be in GCS ERA5 data set valid range(0, 360), but got longitude_range: {longitude_range}")
    else:
        if longitude_range[0] < -180 or longitude_range[1] < -180 or longitude_range[0] > 180 or longitude_range[1] > 180:
            raise ValueError(f"longitude_range should be in GCS ERA5 data set valid range(-180, 180), but got longitude_range: {longitude_range}")


def _longitude_range_adjustment(longitude_range):
    return (min(longitude_range), max(longitude_range))


def _time_interval_should_be_positive(time_interval):
    if time_interval <= 0:
        raise ValueError(f"data_steps should be greater than 0, but got {time_interval}")
