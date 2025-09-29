"""Fetch data from NREL's NSRDB database"""

from numpy import array, average
from pandas import DataFrame, to_datetime
from scipy.spatial import cKDTree

try:
    import h5pyd

    import_all = False
except ImportError:
    import_all = True


def fetch_nsrdb_data(
    attrs: list[str],
    year: int,
    lat_lon: tuple[float] | None = None,
    state: str = '',
    county: str = '',
    resolution: str = '',
    get: str = 'max-population',
    save: str = None,
) -> DataFrame | tuple:
    """fetches nsrdb data from nearest coordinates (latitude, longitude)
    or from county in a state matching a particular 'get' metric

    Args:
        attrs (list[str]): attributes to fetch ['air_temperature', 'clearsky_dhi', 'clearsky_dni', 'clearsky_ghi', 'cloud_type', 'coordinates', 'dew_point', 'dhi', 'dni', 'fill_flag', 'ghi', 'meta', 'relative_humidity', 'solar_zenith_angle', 'surface_albedo', 'surface_pressure', 'time_index', 'total_precipitable_water', 'wind_direction', 'wind_speed']
        year (int): year of choice, e.g. 2019
        lat_lon (Tuple[float], optional): (latitude, longitude) to fetch closest data point. Defaults to None.
        state (str, optional): capitalized state name, e.g. 'Texas' . Defaults to ''.
        county (str, optional): capitalized county name, e.g. 'Brazos' . Defaults to ''.
        resolution (str, optional): choose from 'halfhourly', 'hourly', 'daily'. Defaults to ''.
        get (str, optional): Defaults to 'max-population'. From within county choose the data point that matches one of the following. 'max-population', 'max-elevation', 'max-landcover' 'min-population', 'min-elevation', 'min-landcover'

    Returns:
        DataFrame, tuple: Dataframe with output data, (latitude, longitude)
    """

    if import_all:
        print(
            'This is an optional feature. Please install h5pyd, or pip install energiapy[all]'
        )
        return

    # fetches nsrdb data for the year
    nsrdb_data = h5pyd.File(f"/nrel/nsrdb/v3/nsrdb_{str(year)}.h5", 'r')
    time_index = to_datetime(nsrdb_data['time_index'][...].astype(str))

    if lat_lon is not None:
        # get coordinates for all locations
        coords = nsrdb_data['coordinates'][...]

        tree = cKDTree(coords)

        # find the data point closest to latitude and longitude
        def nearest_site(tree, latitude, longitude):
            lat_lon_query = array([latitude, longitude])
            dist, pos = tree.query(lat_lon_query)
            return pos

        idx = nearest_site(tree=tree, latitude=lat_lon[0], longitude=lat_lon[1])

    else:
        # gets coordinates and associated data
        meta = DataFrame(nsrdb_data['meta'][...])
        # data matching state coordinates
        state_data = meta.loc[meta['state'] == str.encode(state)]
        county_data = state_data.loc[
            state_data['county'] == str.encode(county)
        ]  # data matching county

        # splits the get string, e.g. max - population, gives [max,
        # population(get_metric)]
        get_metric = get.split('-')[1]

        if get.split('-')[0] == 'min':
            latitude = float(
                county_data['latitude'][
                    county_data[get_metric] == min(county_data[get_metric])
                ].iloc[0]
            )
            longitude = float(
                county_data['longitude'][
                    county_data[get_metric] == min(county_data[get_metric])
                ].iloc[0]
            )
            loc_data = county_data.loc[
                (county_data['latitude'] == latitude)
                & (county_data['longitude'] == longitude)
            ]

        if get.split('-')[0] == 'max':
            latitude = float(
                county_data['latitude'][
                    county_data[get_metric] == max(county_data[get_metric])
                ].iloc[0]
            )
            longitude = float(
                county_data['longitude'][
                    county_data[get_metric] == max(county_data[get_metric])
                ].iloc[0]
            )
            loc_data = county_data.loc[
                (county_data['latitude'] == latitude)
                & (county_data['longitude'] == longitude)
            ]

        idx = loc_data.index[0]
        lat_lon = (latitude, longitude)

    timestep_dict = {
        'halfhourly': 1,  # native data set at 30 mins
        'hourly': 2,  # averages over the hour
        'daily': 48,  # averages over the day
    }
    averaged_output = DataFrame()

    psm_scale_dict = {
        attr: nsrdb_data[attr].attrs['psm_scale_factor'] for attr in attrs
    }

    for attr in attrs:
        full_output = nsrdb_data[attr][:, idx]  # native data set at 30 mins
        averaged_output[attr] = average(
            full_output.reshape(-1, timestep_dict[resolution]), axis=1
        )  # averages over resolution
    averaged_output = averaged_output.set_index(
        time_index[:: timestep_dict[resolution]]
    )

    for attr in attrs:
        averaged_output[attr] = averaged_output[attr] / psm_scale_dict[attr]

    if save is not None:
        averaged_output.to_csv(save + '.csv')

    return lat_lon, averaged_output
