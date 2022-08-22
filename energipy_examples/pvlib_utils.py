#%%
"""pvlib utils  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"


# import pandas
# from pvlib.pvsystem import PVSystem, retrieve_sam
# from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
# from pvlib.tracking import SingleAxisTracker
# from pvlib.modelchain import ModelChain
# from pvlib.location import Location



# def fetch_nsrdb_data(year:int, state:str, county:str, resolution:str = ''):
f = h5pyd.File(f"/nrel/nsrdb/v3/nsrdb_{str(year)}.h5", 'r') 
# #%%

# import h5pyd
# import numpy 
# import pandas 
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
# from scipy.spatial import cKDTree

# year = 2019
# state = 'Texas'
# county = 'Brazos'
# resolution = 'H'


# time_index = pandas.to_datetime(f['time_index'][...].astype(str))

# if resolution == 'H':
#     # timestep = numpy.where(time_index.month == 1)[0][0]
#     timestep = numpy.where(time_index == '2019-07-04 00:00:00')[0][0]
# else:
#     timestep = time_index 
# #%%
# meta = pandas.DataFrame(f['meta'][...]) 
# state_data = meta.loc[meta['state'] == str.encode(state)]
# county_data = state_data.loc[state_data['county'] == str.encode(county)]
# # print(meta.head())
# # coords = f['coordinates'][...]
# latitude = float(county_data['latitude'][county_data['population'] == max(county_data['population'])])
# longitude = float(county_data['longitude'][county_data['population'] == max(county_data['population'])])
# loc_data = county_data.loc[(county_data['latitude'] == latitude) & (county_data['longitude'] == longitude)]
# # ghi = f['ghi'][timestep][loc_data.index]

# #%%
# dset = f['ghi']
# coords = f['coordinates'][...]
# data = dset[timestep, ::10]   # extract every 10th location at a particular time
# df = pandas.DataFrame() # Combine data with coordinates in a DataFrame
# df['longitude'] = coords[::10, 1]
# df['latitude'] = coords[::10, 0]
# df['ghi'] = data / dset.attrs['psm_scale_factor']





def solar_power_output(file_name):
    """Calculates solar power output using weather data
  Relevant factors include DHI (W/m2), DNI (W/m2), GHI (W/m2), 
  Temperature (C), Dewpoint (C), Relative humidity (%)

    Args:
        loc_ (str): location 
        yr_ (str): year

    Returns:
        df_ (DataFrame): a dataframe with hourly solar power outputs
    """

    file_ = 'NSRDB'+ loc_ + yr_ + '.csv'

    df_ = pandas.read_csv(file_, nrows=2)

    latitude_ = float(df_.Latitude[0])
    longitude_ = float(df_.Longitude[0])

    coord_ = [latitude_, longitude_ ]

    df_ = pandas.read_csv(file_,
                    skiprows=2,
                    usecols=['Year', 'Month', 'Day', 'Hour', 'Minute', 'DHI', 'DNI', 'GHI',
                            'Wind Speed', 'Temperature', 'Dew Point', 'Relative Humidity'],
                    index_col='datetime',
                    parse_dates={'datetime': ['Year', 'Month', 'Day', 'Hour', 'Minute']},
                    date_parser=lambda x: datetime.datetime.strptime(x, '%Y %m %d %H %M')
                    )
    df_ = df_.dropna()

    df_ = df_.loc[:, ['DHI', 'DNI', 'GHI', 'Wind Speed', 'Temperature',
                'Dew Point', 'Relative Humidity']]

    df_.columns = ['dhi', 'dni', 'ghi', 'wind_speed', 'temp_air', 'temp_dew', 'relative_humidity']
    df_ = df_.resample('H').mean()
    modules = retrieve_sam('cecmod')
    module_parameters = modules['Canadian_Solar_Inc__CS5P_220M']
    inverters = retrieve_sam('cecinverter')
    inverter_parameters = inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']
    tparams = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    system = PVSystem(
    module_parameters=module_parameters,
    inverter_parameters=inverter_parameters,
    temperature_model_parameters=tparams)
    location = Location(latitude=coord_[0], longitude=coord_[1])
    mc = ModelChain(system, location, aoi_model = 'no_loss',
    ac_model = 'sandia', spectral_model= 'no_loss')
    mc.run_model(weather=df_)
    output_ = pandas.DataFrame(np.maximum(0, np.nan_to_num(np.array(mc.ac))), index = df_.index)
    return output_
# solar = solar_power_output('ho', '19')
# solar = solar_power_output('la', '19')

#%%

hsconfigure

# %%
# %%

# %%



# %%
