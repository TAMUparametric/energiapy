"""Cost scenario data class  
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
class cost_scenario:
    """
    Onject with data regarding a cost scenario
    """

    def __init__(self, name: str, horizon: float, label: str = '', enterprise: float = '', utility: float = '', pilot: float = '', repurposed: float = ''):
        """cost scenario parameters

        Args:
            name (str): ID for the cost scenario
            label (str, optional): name of the location. Defaults to ''.
            horizon (float): length of planning horizon
            enterprise (float, optional): reduction in cost over horizon for enterprise TRL. Defaults to ''.
            utility (float, optional): reduction in cost over horizon for utility TRL. Defaults to ''.
            pilot (float, optional): reduction in cost over horizon for pilot TRL. Defaults to ''.
            repurposed (float, optional): reduction in cost over horizon for repurposed TRL. Defaults to ''.
        """
        self.name = name
        self.label = label
        self.horizon = horizon
        self.enterprise = enterprise
        self.utility = utility
        self.pilot = pilot
        self.repurposed = repurposed

    def __repr__(self):
        return self.name