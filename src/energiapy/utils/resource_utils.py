"""Model utilities
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from ..components.resource import Resource


def create_storage_resource(process_name: str, resource: Resource, store_max: float = 0,
                            store_min: float = 0) -> Resource:
    """Creates a dummy resource for storage, used if process is storage type

    Args:
        resource (Resource): Dummy resource name derived from stored resource
        store_max (float, optional): Maximum amount of resource that can be stored. Defaults to 0.
        store_min (float, optional): Minimum amount of resource that can be stored. Defaults to 0.

    Returns:
        Resource: Dummy resource for storage
    """
    resource_dummy = Resource(name=f"{process_name}_{resource.name}_stored", loss=resource.loss, store_max=store_max,
                              store_min=store_min, basis=resource.basis, block=resource.block + '(stored)',
                              label=resource.label + f"{process_name}(stored)")

    return resource_dummy
