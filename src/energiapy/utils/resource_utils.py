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

from ..components.resource import Resource



def create_storage_resource(resource: Resource, store_max: float = 0, store_min: float = 0) -> Resource:
    """Creates a dummy resource for storage, used if process is storage type

    Args:
        resource (Resource): Dummy resource name derived from stored resource
        store_max (float, optional): Maximum amount of resource that can be stored. Defaults to 0.
        store_min (float, optional): Minimum amount of resource that can be stored. Defaults to 0.

    Returns:
        Resource: Dummy resource for storage
    """
    resource_dummy = Resource(name= resource.name+'_stored', loss= resource.loss, store_max= store_max, store_min= store_min, basis= resource.basis, block= resource.block+'(stored)', label= resource.label+'(stored)')
    
    return resource_dummy

