"""Location data class  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass


@dataclass
class location:
    """
    Object with data regarding a location
    """

    def __init__(self, name: str, label: str = '', PV_class: str = '', WF_class: str = '', LiI_class: str = '', PSH_class: str = ''):
        """location object parameters

        Args:
            name (str): ID for locations
            label (str, optional): name of the location. Defaults to ''.
            PV_class (str, optional): Residential solar PV costing class based on average availability (DOE/NRELatb). Defaults to ''.
            WF_class (str, optional): Wind costing class based on average availability (DOE/NRELatb). Defaults to ''.
            LiI_class (str, optional): Charging cycle for lithium ion batteries (NRELatb). Defaults to ''.
            PSH_class (str, optional): PSH category (NRELatb). Defaults to ''.
        """
        self.name = name
        self.label = label
        self.PV_class = PV_class
        self.WF_class = WF_class
        self.LiI_class = LiI_class
        self.PSH_class = PSH_class

    def __repr__(self):
        return self.name
