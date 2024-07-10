
from .resource import Resource
# from .process import Process
# from .location import Location
from .temporal_scale import TemporalScale

from dataclasses import dataclass


@dataclass
class Problem:
    name: str = None
    scales: TemporalScale = None
    resources: list = None
    processes: list = None

    def __post_init__(self):
        if not self.name:
            self.name = 'Problem'
        self.resources = list()
        # self.processes = list()

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        # if hasattr(getattr(self, name), 'ctype'):
        if isinstance(getattr(self, name), TemporalScale):
            setattr(getattr(self, name), 'name', name)
            if not self.scales:
                self.scales = getattr(self, name)
        if isinstance(getattr(self, name), Resource):
            setattr(getattr(self, name), 'name', name)
            setattr(getattr(self, name), 'scales', self.scales)
            
            # if getattr(self, name).scales is None:
            # getattr(self, name).scales = self.scales
            self.resources.append(getattr(self, name))
        # if isinstance(getattr(self, name), Process):
        #     setattr(getattr(self, name), 'name', name)
        #     self.processes.append(getattr(self, name))
