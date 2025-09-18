"""Process conversion models (external libraries)"""

import numpy as np
import pandas as pd
from pvlib.location import Location as PVLocation
from pvlib.modelchain import ModelChain as PVModelChain
from pvlib.pvsystem import PVSystem, retrieve_sam
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from windpowerlib import ModelChain as WModelChain
from windpowerlib import WindTurbine


def solar_power_output(
    data: pd.DataFrame,
    coord: tuple,
    sam: str = 'cecmod',
    module_params: str = 'Canadian_Solar_Inc__CS5P_220M',
    inverter: str = 'cecinverter',
    inverter_params: str = 'ABB__MICRO_0_25_I_OUTD_US_208__208V_',
    temperature_params: str = 'open_rack_glass_glass',
    aoi_model: str = 'no_loss',
    ac_model: str = 'sandia',
    spectral_model: str = 'no_loss',
):
    """Calculates solar power output using weather data
    Relevant factors include DHI (W/m2), DNI (W/m2), GHI (W/m2),
    Temperature (C), Dewpoint (C), Relative humidity (%)

    Args:
        data (pd.DataFrame): weather data input with dni, dhi, wind_speed, ghi, air_temperature, dew_point, relative_humidity
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
        temperature_model_parameters=tparams,
    )
    location = PVLocation(latitude=coord[0], longitude=coord[1])
    mc = PVModelChain(
        system,
        location,
        aoi_model=aoi_model,
        ac_model=ac_model,
        spectral_model=spectral_model,
    )
    mc.run_model(weather=data)
    # make a list, avoid np.float64
    array = np.maximum(0, np.nan_to_num(np.array(mc.results.ac)))
    return [float(i) for i in array]


def wind_power_output(
    data: pd.DataFrame,
    roughness_length: float = 0.1,
    turbine_type: str = 'V100/1800',
    hub_height: float = 92,
    wind_speed_model: str = 'logarithmic',
    density_model: str = 'ideal_gas',
    temperature_model: str = 'linear_gradient',
    power_output_model: str = 'power_coefficient_curve',
    density_correction: bool = True,
    obstacle_height: float = 0,
    observation_height: float = 10,
):
    """Calculates wind power output using weather data
    Relevant factors include wind speeds (m/s), temperature (K), and pressure(Pa)

    Args:
        data (pd.DataFrame): weather data input with wind_speed, air_temperature, surface_pressure
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

    data['pressure'] = 100 * data['surface_pressure']
    data['temperature'] = data['air_temperature'] + 273.15
    data['roughness_length'] = roughness_length

    # data = data.resample('H').mean()
    data = pd.DataFrame(
        data[['wind_speed', 'temperature', 'pressure', 'roughness_length']].to_numpy(),
        index=data.index,
        columns=[
            np.array(['wind_speed', 'temperature', 'pressure', 'roughness_length']),
            np.array([observation_height, observation_height, observation_height, 0]),
        ],
    )
    # specification of wind turbine where power curve is provided in the
    # oedb turbine library
    turbine_type_ = {
        'turbine_type': turbine_type,  # Vestas
        'hub_height': hub_height,  # in m
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
        'hellman_exp': None,
    }  # None (default) or None
    # initialize ModelChain with own specifications and use run_model method to
    # calculate power output
    mc_turbine = WModelChain(turbine, **modelchain_data).run_model(data)
    return list(mc_turbine.power_output)
