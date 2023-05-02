"""Windpowerlib
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
from windpowerlib import WindTurbine
from windpowerlib import ModelChain as WModelChain


def wind_power_output(data: pandas.DataFrame, roughness_length: float = 0.1, turbine_type: str = 'V100/1800', hub_height: float = 92, wind_speed_model: str = 'logarithmic', density_model: str = 'ideal_gas', temperature_model: str = 'linear_gradient', power_output_model: str = 'power_coefficient_curve', density_correction: bool = True, obstacle_height: float = 0, observation_height: float = 10):
    """Calculates wind power output using weather data
    Relevant factors include wind speeds (m/s), temperature (K), and pressure(Pa)

    Args:
        data (pandas.DataFrame): weather data input with wind_speed, air_temperature, surface_pressure
        roughness_length (float, optional): Defaults to 0.1.
        turbine_type (str, optional): Defaults to 'V100/1800'.
        hub_height (float, optional): Defaults to 92.
        wind_speed_model (str, optional): Defaults to 'logarithmic'.
        density_model (str, optional): Defaults to 'ideal_gas'.
        temperature_model (str, optional): Defaults to 'linear_gradient'.
        power_output_model (str, optional): Defaults to power_coefficient_curve.
        density_correction (bool, optional): Defaults to True.
        obstacle_height (float, optional): Defaults to 0.
        observation_height (float, optional): Defaults to 10.

    Returns:
        output (DataFrame): a dataframe with hourly wind power outputs
    """

    # df_ = df_.dropna()

    data['pressure'] = 100*data['surface_pressure']
    data['temperature'] = data['air_temperature'] + 273.15
    data['roughness_length'] = roughness_length

    data = data.resample('H').mean()
    data = pandas.DataFrame(data[['wind_speed', 'temperature', 'pressure', 'roughness_length']].to_numpy(),
                            index=data.index, columns=[numpy.array(['wind_speed', 'temperature', 'pressure', 'roughness_length']), numpy.array([observation_height, observation_height, observation_height, 0])])
    # specification of wind turbine where power curve is provided in the
    # oedb turbine library
    turbine_type_ = {
        'turbine_type': turbine_type,  # Vestas
        'hub_height': hub_height  # in m
    }
    # initialize WindTurbine object
    turbine = WindTurbine(**turbine_type_)

    modelchain_data = {
        'wind_speed_model': wind_speed_model,  # 'logarithmic' (default),
        # 'hellman' or
        # 'interpolation_extrapolation'
        'density_model': density_model,  # 'barometric' (default), 'ideal_gas'
        # or 'interpolation_extrapolation'
        'temperature_model': temperature_model,  # 'linear_gradient' (def.) or
        # 'interpolation_extrapolation'
        # 'power_curve' (default) or
        'power_output_model': power_output_model,
        # 'power_coefficient_curve'
        'density_correction': density_correction,  # False (default) or True
        'obstacle_height': obstacle_height,  # default: 0
        'hellman_exp': None}  # None (default) or None
    # initialize ModelChain with own specifications and use run_model method to
    # calculate power output
    mc_turbine = WModelChain(turbine, **modelchain_data).run_model(data)
    # write power output time series to WindTurbine object
    output = pandas.DataFrame(mc_turbine.power_output)
    return output
