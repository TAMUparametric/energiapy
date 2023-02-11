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


from itertools import count
from xml.sax.handler import feature_external_ges
import h5pyd
import numpy 
import pandas 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from scipy.spatial import cKDTree
from typing import List, Tuple, Union


def fetch_nsrdb_data(attrs: List[str], year:int, lat_lon:Tuple[float] = None, state:str = '', \
    county:str = '', resolution:str = '', get:str = 'max-population', save:str = None) -> Union[pandas.DataFrame, tuple]:
    """fetches nsrdb data from nearest coordinates (latitude, longitude) 
    or from county in a state matching a particular 'get' metric

    Args:
        attrs (List[str]): attributes to fetch ['air_temperature',
                                        'clearsky_dhi',
                                        'clearsky_dni',
                                        'clearsky_ghi',
                                        'cloud_type',
                                        'coordinates',
                                        'dew_point',
                                        'dhi',
                                        'dni',
                                        'fill_flag',
                                        'ghi',
                                        'meta',
                                        'relative_humidity',
                                        'solar_zenith_angle',
                                        'surface_albedo',
                                        'surface_pressure',
                                        'time_index',
                                        'total_precipitable_water',
                                        'wind_direction',
                                        'wind_speed']
        year (int): year of choice, e.g. 2019
        lat_lon (Tuple[float], optional): (latitude, longitude) to fetch closest data point. Defaults to None.
        state (str, optional): capitalized state name, e.g. 'Texas' . Defaults to ''.
        county (str, optional): capitalized county name, e.g. 'Brazos' . Defaults to ''.
        resolution (str, optional): choose from 'halfhourly', 'hourly', 'daily'. Defaults to ''.
        get (str, optional): Defaults to 'max-population'. 
                            From within county choose the data point that matches one of the following. 
                            'max-population', 'max-elevation', 'max-landcover'
                            'min-population', 'min-elevation', 'min-landcover' 
                             
    Returns:
        pandas.DataFrame, tuple: Dataframe with data, (latitude, longitude)
    """
    
    
    nsrdb_data = h5pyd.File(f"/nrel/nsrdb/v3/nsrdb_{str(year)}.h5", 'r') #fetches nsrdb data for the year
    time_index = pandas.to_datetime(nsrdb_data['time_index'][...].astype(str))
    
    
    if lat_lon is not None:    
        coords = nsrdb_data['coordinates'][...] #get coordinates for all locations

        tree = cKDTree(coords)
        
        def nearest_site(tree, latitude, longitude): # find the data point closest to latitude and longitude
            lat_lon_query = numpy.array([latitude, longitude])
            dist, pos = tree.query(lat_lon_query)
            return pos

        idx = nearest_site(tree = tree, latitude = lat_lon[0], longitude = lat_lon[1])

    else:
        meta = pandas.DataFrame(nsrdb_data['meta'][...]) #gets coordinates and associated data 
        state_data = meta.loc[meta['state'] == str.encode(state)] #data matching state coordinates
        county_data = state_data.loc[state_data['county'] == str.encode(county)] # data matching county

        get_metric = get.split('-')[1] # splits the get string, e.g. max - population, gives [max, population(get_metric)]
        
        if get.split('-')[0] == 'min':
            latitude = float(county_data['latitude'][county_data[get_metric] == min(county_data[get_metric])])
            longitude = float(county_data['longitude'][county_data[get_metric] == min(county_data[get_metric])])
            loc_data = county_data.loc[(county_data['latitude'] == latitude) & (county_data['longitude'] == longitude)]
        
        if get.split('-')[0] == 'max':
            latitude = float(county_data['latitude'][county_data[get_metric] == max(county_data[get_metric])])
            longitude = float(county_data['longitude'][county_data[get_metric] == max(county_data[get_metric])])
            loc_data = county_data.loc[(county_data['latitude'] == latitude) & (county_data['longitude'] == longitude)]
        
        idx = loc_data.index[0]
        lat_lon = (latitude, longitude)
    
    timestep_dict = {
        'halfhourly' : 1, #native data set at 30 mins 
        'hourly' : 2, #averages over the hour
        'daily' : 48, #averages over the day
        }
    averaged_output = pandas.DataFrame()
    for attr in attrs:
        full_output = nsrdb_data[attr][:, idx] #native data set at 30 mins
        averaged_output[attr] = numpy.average(full_output.reshape(-1, timestep_dict[resolution]), axis = 1) #averages over resolution
    averaged_output = averaged_output.set_index(time_index[::timestep_dict[resolution]])
    
    if save is not None:
        averaged_output.to_csv(save+ '.csv')
        
    return lat_lon, averaged_output
#%%

#%%

from pvlib.pvsystem import PVSystem, retrieve_sam
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from pvlib.tracking import SingleAxisTracker
from pvlib.modelchain import ModelChain
from pvlib.location import Location



def solar_power_output(weather_df: pandas.DataFrame, lat_lon = tuple):
    weather_df = weather_df.rename(columns = {'air_temperature': 'temp_air', 'dew_point': 'temp_dew'}) #rename for pvlib purposes
    modules = retrieve_sam('cecmod')
    module_parameters = modules['Canadian_Solar_Inc__CS5P_220M']
    inverters = retrieve_sam('cecinverter')
    inverter_parameters = inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']
    tparams = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    system = PVSystem(
    module_parameters=module_parameters,
    inverter_parameters=inverter_parameters,
    temperature_model_parameters=tparams)
    location = Location(latitude=lat_lon[0], longitude=lat_lon[1])
    mc = ModelChain(system, location, aoi_model = 'no_loss',
    ac_model = 'sandia', spectral_model= 'no_loss')
    mc.run_model(weather=weather_df)
    output_ = pandas.DataFrame(numpy.maximum(0, numpy.nan_to_num(numpy.array(mc.results.ac))), index = weather_df.index)
    # output_ = pandas.DataFrame(numpy.nan_to_num(numpy.array(mc.results.ac)), index = weather_df.index)
    
    return output_
# solar = solar_power_output('ho', '19')

#%%