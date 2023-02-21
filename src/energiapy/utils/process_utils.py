"""Model utilities  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"


from ..components.process import Process


def create_storage_process(process) -> Process:
    """Creates a dummy process for discharge of stored resource

    Args:
        process (Process): Dummy process name derived from storage process
    Returns:
        Process: Dummy process for storage
    """
    process_dummy = Process(name= process.name+'_discharge', conversion = process.conversion_discharge, prod_min= process.prod_min, \
        prod_max= process.prod_max, introduce= process.introduce, retire= process.retire, lifetime= process.lifetime, label = process.label +'_storage')
    return process_dummy


