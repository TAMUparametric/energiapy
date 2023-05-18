"""PVLib
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.1.0"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

import pandas
import numpy
from pvlib.pvsystem import PVSystem, retrieve_sam
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from pvlib.modelchain import ModelChain as PVModelChain
from pvlib.location import Location as PVLocation


def solar_power_output(data: pandas.DataFrame, coord: tuple, sam: str = 'cecmod', module_params: str = 'Canadian_Solar_Inc__CS5P_220M', inverter: str = 'cecinverter', inverter_params: str = 'ABB__MICRO_0_25_I_OUTD_US_208__208V_', temperature_params: str = 'open_rack_glass_glass', aoi_model: str = 'no_loss', ac_model: str = 'sandia', spectral_model: str = 'no_loss'):
    """Calculates solar power output using weather data
    Relevant factors include DHI (W/m2), DNI (W/m2), GHI (W/m2), 
    Temperature (C), Dewpoint (C), Relative humidity (%)

    Args:
        data (pandas.DataFrame): weather data input with dni, dhi, wind_speed, ghi, air_temperature, dew_point, relative_humidity 
        coord (tuple): latitude and longitude
        sam (str, optional): Defaults to 'cecmod'.
        module_parameters (str, optional): Defaults to 'Canadian_Solar_Inc__CS5P_220M'.
        inverter (str, optional):  Defaults to 'cecinverter'.
        inverter_parameters (str, optional): Defaults to 'ABB__MICRO_0_25_I_OUTD_US_208__208V_'.
        temperature_params (str, optional): Defaults to 'open_rack_glass_glass'.
        aoi_model (str, optional): Defaults to 'no_loss'.
        ac_model (str, optional): Defaults to 'sandia'.
        spectral_model (str, optional): Defaults to 'no_loss'.

    Returns:
        output (DataFrame): a dataframe with hourly solar power outputs
    """
    # data = data.resample('H').mean()

    modules = retrieve_sam(sam)
    module_parameters = modules[module_params]
    inverters = retrieve_sam(inverter)
    inverter_parameters = inverters[inverter_params]
    tparams = TEMPERATURE_MODEL_PARAMETERS['sapm'][temperature_params]
    system = PVSystem(
        module_parameters=module_parameters,
        inverter_parameters=inverter_parameters,
        temperature_model_parameters=tparams)
    location = PVLocation(latitude=coord[0], longitude=coord[1])
    mc = PVModelChain(system, location, aoi_model=aoi_model,
                      ac_model=ac_model, spectral_model=spectral_model)
    mc.run_model(weather=data)
    output = pandas.DataFrame(numpy.maximum(0, numpy.nan_to_num(
        numpy.array(mc.results.ac))), index=data.index)
    output.columns = ['PV_Power']
    return output
