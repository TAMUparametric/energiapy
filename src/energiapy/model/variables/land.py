from pyomo.environ import ConcreteModel

from .variables import generate_var_loc_com_scn


def generate_land_vars(instance: ConcreteModel):
    """variables for land usage and costs

    Args:
        instance (ConcreteModel): pyomo instance
    """
    generate_var_loc_com_scn(instance=instance, var_name='Land',
                             tag='process', component_set='processes', label='Land use ')

    generate_var_loc_com_scn(instance=instance, var_name='Land_cost',
                             tag='process', component_set='processes', label='Land expenditure')
