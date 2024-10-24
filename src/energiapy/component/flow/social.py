"""Social Impact"""

from dataclasses import dataclass, fields, field


@dataclass
class Social:
    """Social Impact Metric"""

    # Setup and Disposal at Locations, Linkages
    benefit: dict = field(default=None)
    detriment: dict = field(default=None)

    @staticmethod
    def inputs():
        """Inputs"""
        return ['benefit', 'detriment']

    @property
    def uses(self):
        """Land Uses across the Scenario"""
        return self.taskmaster.report_use
